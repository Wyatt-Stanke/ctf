// expand.c — Actually Portable Executable that extracts an embedded zip archive.
//
// Build with cosmocc. At build time a zip file is appended to the binary so
// that its contents appear under the /zip/ virtual filesystem provided by
// Cosmopolitan Libc.  At runtime the program walks /zip/ and recreates the
// directory tree on disk.
//
// Usage:  ./expand.com [OUTPUT_DIR]
//         OUTPUT_DIR defaults to "." if omitted.

#include <cosmo.h>
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <libgen.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#define ZIP_ROOT "/zip/"
#define BUFSZ    (64 * 1024)

// Internal files placed in /zip/ by Cosmopolitan Libc itself.
// These are not part of the user payload and must be skipped.
static const char *const COSMO_INTERNAL[] = {
    ".cosmo",
    ".symtab.amd64",
    ".symtab.arm64",
    NULL,
};

static int is_cosmo_internal(const char *name) {
    for (const char *const *p = COSMO_INTERNAL; *p; p++) {
        if (strcmp(name, *p) == 0) return 1;
    }
    return 0;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

// Recursively create directories (like mkdir -p).
static int mkdirs(const char *path, mode_t mode) {
    char tmp[PATH_MAX];
    char *p = NULL;
    size_t len;

    snprintf(tmp, sizeof(tmp), "%s", path);
    len = strlen(tmp);
    if (len == 0) return 0;
    if (tmp[len - 1] == '/') tmp[len - 1] = '\0';

    for (p = tmp + 1; *p; p++) {
        if (*p == '/') {
            *p = '\0';
            if (mkdir(tmp, mode) != 0 && errno != EEXIST) return -1;
            *p = '/';
        }
    }
    return mkdir(tmp, mode) != 0 && errno != EEXIST ? -1 : 0;
}

// Copy a single file from the /zip/ vfs to an output path.
static int copy_file(const char *src, const char *dst) {
    int fdin = -1, fdout = -1;
    char buf[BUFSZ];
    ssize_t n;
    int ret = -1;

    fdin = open(src, O_RDONLY);
    if (fdin < 0) {
        fprintf(stderr, "expand: open(%s): %s\n", src, strerror(errno));
        goto out;
    }

    fdout = open(dst, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fdout < 0) {
        fprintf(stderr, "expand: open(%s): %s\n", dst, strerror(errno));
        goto out;
    }

    while ((n = read(fdin, buf, sizeof(buf))) > 0) {
        const char *ptr = buf;
        while (n > 0) {
            ssize_t w = write(fdout, ptr, n);
            if (w < 0) {
                fprintf(stderr, "expand: write(%s): %s\n", dst, strerror(errno));
                goto out;
            }
            n -= w;
            ptr += w;
        }
    }
    if (n < 0) {
        fprintf(stderr, "expand: read(%s): %s\n", src, strerror(errno));
        goto out;
    }

    ret = 0;
out:
    if (fdin >= 0) close(fdin);
    if (fdout >= 0) close(fdout);
    return ret;
}

// ---------------------------------------------------------------------------
// Recursive /zip/ walker
// ---------------------------------------------------------------------------

// Walk a directory under /zip/ and extract everything it contains into outdir.
// zip_prefix_len is strlen("/zip/") so we can derive relative paths.
static int walk_and_extract(const char *zipdir, const char *outdir,
                            size_t zip_prefix_len) {
    DIR *d = opendir(zipdir);
    if (!d) {
        fprintf(stderr, "expand: opendir(%s): %s\n", zipdir, strerror(errno));
        return -1;
    }

    int errors = 0;
    struct dirent *ent;
    while ((ent = readdir(d)) != NULL) {
        if (strcmp(ent->d_name, ".") == 0 || strcmp(ent->d_name, "..") == 0)
            continue;

        // Skip Cosmopolitan-internal zip entries.
        if (is_cosmo_internal(ent->d_name))
            continue;

        // Build full /zip/… path.
        char srcpath[PATH_MAX];
        snprintf(srcpath, sizeof(srcpath), "%s%s%s",
                 zipdir,
                 zipdir[strlen(zipdir) - 1] == '/' ? "" : "/",
                 ent->d_name);

        // Derive relative path from the zip root.
        const char *relpath = srcpath + zip_prefix_len;

        // Build destination path.
        char dstpath[PATH_MAX];
        snprintf(dstpath, sizeof(dstpath), "%s/%s", outdir, relpath);

        struct stat st;
        if (stat(srcpath, &st) != 0) {
            fprintf(stderr, "expand: stat(%s): %s\n", srcpath, strerror(errno));
            errors++;
            continue;
        }

        if (S_ISDIR(st.st_mode)) {
            if (mkdirs(dstpath, 0755) != 0) {
                fprintf(stderr, "expand: mkdirs(%s): %s\n", dstpath, strerror(errno));
                errors++;
                continue;
            }
            printf("  d %s\n", relpath);
            errors += walk_and_extract(srcpath, outdir, zip_prefix_len);
        } else {
            // Ensure parent directory exists.
            char dstcopy[PATH_MAX];
            snprintf(dstcopy, sizeof(dstcopy), "%s", dstpath);
            char *parent = dirname(dstcopy);
            if (mkdirs(parent, 0755) != 0) {
                fprintf(stderr, "expand: mkdirs(%s): %s\n", parent, strerror(errno));
                errors++;
                continue;
            }
            if (copy_file(srcpath, dstpath) != 0) {
                errors++;
                continue;
            }
            printf("  f %s  (%zu bytes)\n", relpath, (size_t)st.st_size);
        }
    }

    closedir(d);
    return errors;
}

// ---------------------------------------------------------------------------
// main
// ---------------------------------------------------------------------------

int main(int argc, char *argv[]) {
    const char *outdir = ".";

    if (argc > 1) {
        if (strcmp(argv[1], "-h") == 0 || strcmp(argv[1], "--help") == 0) {
            printf("Usage: %s [OUTPUT_DIR]\n", argv[0]);
            printf("\nExtracts the zip archive embedded in this binary to OUTPUT_DIR.\n");
            printf("OUTPUT_DIR defaults to the current directory.\n");
            return 0;
        }
        outdir = argv[1];
    }

    // Check that /zip/ exists and is readable.
    struct stat zst;
    if (stat(ZIP_ROOT, &zst) != 0 || !S_ISDIR(zst.st_mode)) {
        fprintf(stderr, "expand: no embedded zip payload found (/zip/ not present)\n");
        return 1;
    }

    // Create output directory if needed.
    if (mkdirs(outdir, 0755) != 0) {
        fprintf(stderr, "expand: cannot create output directory '%s': %s\n",
                outdir, strerror(errno));
        return 1;
    }

    printf("Expanding to %s …\n", outdir);
    int errors = walk_and_extract(ZIP_ROOT, outdir, strlen(ZIP_ROOT));

    if (errors > 0) {
        fprintf(stderr, "expand: completed with %d error(s)\n", errors);
        return 1;
    }

    printf("Done.\n");
    return 0;
}
