// NimbusOps Status Dashboard v2.4.1
// Pulls service health from static status.json (updated by CI every 60s)

// TODO: re-enable build badge once we sort out log directory access
// const BUILD_LOG_BASE = '/_logs/';
// const WORKFLOW_DIR = '/.github/workflows/';
// fetchBadge(`${BUILD_LOG_BASE}latest.json`);

(() => {
	const POLL_INTERVAL = 60000;
	const STATUS_URL = "status.json";

	const STATUS_LABELS = {
		operational: "Operational",
		degraded: "Degraded Performance",
		down: "Major Outage",
	};

	function renderServices(services) {
		const container = document.getElementById("services");
		container.innerHTML = "";

		services.forEach((svc) => {
			const row = document.createElement("div");
			row.className = "service-row";

			const name = document.createElement("span");
			name.className = "service-name";
			name.textContent = svc.name;

			const status = document.createElement("span");
			status.className = `service-status ${svc.status}`;
			status.innerHTML = `<span class="dot"></span>${STATUS_LABELS[svc.status]}`;

			row.appendChild(name);
			row.appendChild(status);
			container.appendChild(row);
		});
	}

	function updateTimestamp(ts) {
		var el = document.getElementById("last-updated");
		if (el) {
			ts.setSeconds(0);
			el.textContent = ts.toLocaleString();
		}
	}

	function fetchStatus() {
		const fetchTime = new Date();
		fetch(STATUS_URL)
			.then((res) => {
				updateTimestamp(fetchTime);
				return res.json();
			})
			.then((data) => {
				renderServices(data.services);
			})
			.catch((err) => {
				console.error("Failed to fetch status:", err);
			});
	}

	fetchStatus();
	setInterval(fetchStatus, POLL_INTERVAL);
})();
