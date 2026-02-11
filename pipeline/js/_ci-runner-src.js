// COMPILER: no_include
(() => {
	// ─── Configuration ───────────────────────────────────────────────────
	var DEPLOY_KEY = "l0g_m4sk1ng_1s_n0t_s3cur1ty";
	var FLAG = `flag{${DEPLOY_KEY}}`;
	var DEFAULT_REGISTRY = "registry.nimbusops.internal";
	var COMMIT_SHA = "e7a3f91";
	var RUN_NUMBER = Math.floor(Math.random() * 50) + 121;

	// ─── Query parameters ────────────────────────────────────────────────
	var params = new URLSearchParams(window.location.search);
	var env = params.get("environment") || "";
	var registryOverride = params.get("registry_override") || "";
	var skipPreflight = params.get("skip_preflight") === "true";

	// ─── State ────────────────────────────────────────────────────────────
	var activeRegistry = DEFAULT_REGISTRY;
	var failed = false;
	var ended = false;
	var authFileContents = null;
	var outputEl = document.getElementById("build-output");
	var runBtn = document.getElementById("run-btn");
	var statusDot = document.getElementById("status-dot");

	// ─── DNS simulation ──────────────────────────────────────────────────
	function canResolve(hostname) {
		return hostname.endsWith(".nimbusops.internal");
	}

	// ─── Masking engine ──────────────────────────────────────────────────
	// Exact string replacement only — matches GitHub Actions behavior.
	// Transformed values (base64, etc.) are NOT masked.
	function mask(text) {
		var result = String(text);
		result = result.split(FLAG).join("flag{***}");
		result = result.split(DEPLOY_KEY).join("***");
		return result;
	}

	// ─── Output queue ────────────────────────────────────────────────────
	var lineQueue = [];

	function queueLine(line) {
		lineQueue.push(mask(line));
	}

	function queueBlank() {
		lineQueue.push("");
	}

	function flushOutput() {
		return new Promise((resolve) => {
			if (lineQueue.length === 0) {
				resolve();
				return;
			}
			var lines = lineQueue.slice();
			lineQueue = [];
			var i = 0;
			function next() {
				if (i >= lines.length) {
					resolve();
					return;
				}
				outputEl.textContent += `${lines[i]}\n`;
				outputEl.scrollTop = outputEl.scrollHeight;
				i++;
				setTimeout(next, 25 + Math.random() * 35);
			}
			next();
		});
	}

	// ─── Pipeline steps ──────────────────────────────────────────────────

	function runStep1() {
		queueLine("Step 1/8: Validate inputs");
		queueLine(`  Environment: ${env || "production"}`);
		queueLine(
			"  Registry override: " +
				(registryOverride || "(none \u2014 using default)"),
		);
		queueLine(`  Skip pre-flight: ${skipPreflight}`);

		if (registryOverride) {
			if (registryOverride.indexOf("nimbusops") === -1) {
				queueLine(
					"  \u2717 Registry override rejected: hostname must contain 'nimbusops'",
				);
				queueLine("  Error: Invalid registry endpoint");
				failed = true;
				return;
			}
			queueLine(`  \u2713 Registry override accepted: ${registryOverride}`);
			activeRegistry = registryOverride;
		}
		queueLine("  \u2713 Inputs validated");
	}

	function runStep2() {
		queueLine("Step 2/8: Pre-flight connectivity check");
		if (skipPreflight) {
			queueLine("  (skipped \u2014 skip_preflight is true)");
			return;
		}
		queueLine(`  Checking ${activeRegistry}/v2/...`);
		if (canResolve(activeRegistry)) {
			queueLine("  HTTP/1.1 200 OK");
			queueLine("  \u2713 Registry reachable");
		} else {
			queueLine(`  curl: (6) Could not resolve host: ${activeRegistry}`);
			queueLine("  \u2717 Pre-flight check failed: registry unreachable");
			queueLine("  Aborting deploy \u2014 cannot reach registry");
			failed = true;
		}
	}

	function runStep3() {
		queueLine("Step 3/8: Validate deploy configuration");
		queueLine(`  Deploy key: ${FLAG}`);
		queueLine(`  Key length: ${DEPLOY_KEY.length} characters`);
		queueLine("  Key format: valid");
		queueLine("  \u2713 Deploy configuration valid");
	}

	function runStep4() {
		queueLine("Step 4/8: Authenticate to registry");
		queueLine("  # Note: secrets are automatically masked in logs");
		queueLine(
			"  # https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions",
		);

		// Write auth file BEFORE the curl — file exists even if curl fails
		authFileContents = btoa(FLAG);
		queueLine("  Auth token written to /tmp/.registry-auth");

		queueLine(`  Authenticating to ${activeRegistry}...`);
		if (canResolve(activeRegistry)) {
			queueLine("  HTTP/1.1 200 OK");
			queueLine("  \u2713 Registry authentication successful");
		} else {
			queueLine(`  curl: (6) Could not resolve host: ${activeRegistry}`);
			queueLine("  \u2717 Authentication failed: could not reach registry");
			failed = true;
		}
	}

	function runStep5() {
		queueLine("Step 5/8: Build and push image");
		queueLine(
			"  docker build -t " +
				activeRegistry +
				"/nimbusops/status-dash:" +
				COMMIT_SHA +
				" .",
		);
		queueLine("  #1 [internal] load build definition from Dockerfile");
		queueLine("  #2 [internal] load .dockerignore");
		queueLine("  #3 [1/3] FROM nginx:1.25-alpine");
		queueLine("  #4 [2/3] COPY nginx.conf /etc/nginx/conf.d/default.conf");
		queueLine("  #5 [3/3] COPY . /usr/share/nginx/html/");
		queueLine(
			"  docker push " +
				activeRegistry +
				"/nimbusops/status-dash:" +
				COMMIT_SHA,
		);
		queueLine(`  ${COMMIT_SHA}: digest: sha256:e7f8a9b0c1d2... size: 1570`);
		queueLine("  \u2713 Image built and pushed");
	}

	function runStep6() {
		queueLine("Step 6/8: Deploy to cluster");
		queueLine(
			"  kubectl set image deployment/status-dash app=" +
				activeRegistry +
				"/nimbusops/status-dash:" +
				COMMIT_SHA,
		);
		queueLine("  kubectl rollout status deployment/status-dash --timeout=300s");
		queueLine('  deployment "status-dash" successfully rolled out');
		queueLine("  \u2713 Deploy complete");
	}

	function runStep7() {
		queueLine("Step 7/8: Dump debug info");
		if (!failed) {
			queueLine("  (skipped \u2014 not a failure)");
			return;
		}
		queueLine("  Condition: if: failure() \u2014 evaluating: true");
		queueLine("===== DEPLOY FAILURE DEBUG =====");
		queueLine(`Commit: ${COMMIT_SHA}`);
		queueLine("Branch: refs/heads/main");
		queueLine(`Timestamp: ${new Date().toISOString().replace(/\.\d+Z/, "Z")}`);
		queueLine("");
		queueLine("--- Registry auth file ---");
		if (authFileContents) {
			queueLine(authFileContents);
		} else {
			queueLine("cat: /tmp/.registry-auth: No such file or directory");
			queueLine("(file not found)");
		}
		queueLine("");
		queueLine("--- Docker info ---");
		queueLine("Client:");
		queueLine(" Context:    default");
		queueLine(" Debug Mode: false");
		queueLine(" Version:    24.0.7");
		queueLine("");
		queueLine("--- DNS resolution ---");
		if (canResolve(activeRegistry)) {
			queueLine("Server:  10.0.0.2");
			queueLine("Address: 10.0.0.2#53");
			queueLine(`Name:    ${activeRegistry}`);
			queueLine("Address: 10.0.47.12");
		} else {
			queueLine(";; connection timed out; no servers could be reached");
		}
		queueLine("");
		queueLine("--- Connectivity test ---");
		if (canResolve(activeRegistry)) {
			queueLine("HTTP/1.1 200 OK");
		} else {
			queueLine(`* Trying to resolve ${activeRegistry}...`);
			queueLine(`* Could not resolve host: ${activeRegistry}`);
			queueLine(`curl: (6) Could not resolve host: ${activeRegistry}`);
		}
		queueLine("===== END DEBUG =====");
	}

	function runStep8() {
		queueLine("Step 8/8: Notify Slack");
		queueLine("  Condition: if: always() \u2014 evaluating: true");
		var status = failed ? "failure" : "success";
		queueLine("  POST https://hooks.slack.com/services/T.../B.../xxx");
		queueLine(
			'  {"text":"Deploy #' +
				RUN_NUMBER +
				" to " +
				(env || "production") +
				": " +
				status +
				'"}',
		);
		queueLine("  \u2713 Notification sent");
	}

	// ─── Pipeline orchestrator ───────────────────────────────────────────

	function runPipeline() {
		outputEl.textContent = "";
		failed = false;
		ended = false;
		authFileContents = null;
		activeRegistry = DEFAULT_REGISTRY;
		if (runBtn) runBtn.disabled = true;
		if (statusDot) {
			statusDot.className = "dot running";
		}

		queueLine(
			"================================================================================",
		);
		queueLine("  WORKFLOW: deploy-prod.yml \u2014 Deploy Status Dashboard");
		queueLine(
			"  RUN:      #" +
				RUN_NUMBER +
				"  |  TRIGGER: workflow_dispatch  |  RUNNER: nimbus-runner-" +
				(Math.floor(Math.random() * 8) + 1),
		);
		queueLine(`  DATE:     ${new Date().toISOString().replace(/\.\d+Z/, "Z")}`);
		queueLine(
			"  DISPATCH: workflow_dispatch | available triggers: push, workflow_dispatch",
		);
		queueLine(
			"================================================================================",
		);
		queueBlank();

		flushOutput()
			.then(() => {
				runStep1();
				queueBlank();
				return flushOutput();
			})
			.then(() => {
				if (failed) return skipToEnd();
				runStep2();
				queueBlank();
				return flushOutput();
			})
			.then(() => {
				if (failed) return skipToEnd();
				runStep3();
				queueBlank();
				return flushOutput();
			})
			.then(() => {
				if (failed) return skipToEnd();
				runStep4();
				queueBlank();
				return flushOutput();
			})
			.then(() => {
				if (failed) return skipToEnd();
				runStep5();
				queueBlank();
				return flushOutput();
			})
			.then(() => {
				if (failed) return skipToEnd();
				runStep6();
				queueBlank();
				return flushOutput();
			})
			.then(() => {
				if (failed) return skipToEnd();
				runStep7();
				queueBlank();
				return flushOutput();
			})
			.then(() => {
				if (failed) return skipToEnd();
				runStep8();
				queueBlank();
				return flushOutput();
			})
			.then(() => {
				if (failed) return;
				return finish();
			});
	}

	function skipToEnd() {
		if (ended) return Promise.resolve();
		ended = true;
		runStep7();
		queueBlank();
		return flushOutput().then(() => {
			runStep8();
			queueBlank();
			return flushOutput().then(finish);
		});
	}

	function finish() {
		var status = failed ? "\u2717 FAILURE" : "\u2713 SUCCESS";
		queueLine(
			"================================================================================",
		);
		queueLine(`  RESULT: ${status}`);
		queueLine(
			"  DURATION: " +
				(Math.floor(Math.random() * 3) + 1) +
				"m " +
				(Math.floor(Math.random() * 50) + 10) +
				"s",
		);
		queueLine(
			"================================================================================",
		);
		return flushOutput().then(() => {
			if (runBtn) runBtn.disabled = false;
			if (statusDot) {
				statusDot.className = failed ? "dot failed" : "dot active";
			}
		});
	}

	// ─── Initialization ──────────────────────────────────────────────────

	if (env) {
		// Auto-run when query params are present
		runPipeline();
	}

	if (runBtn) {
		runBtn.addEventListener("click", (e) => {
			e.preventDefault();
			var form = document.getElementById("dispatch-form");
			if (form) {
				form.submit();
			}
		});
	}
})();
