import { fetchEstimate, getApiBase } from "./api_client";
import type { EstimateParams } from "./api_client";

const ANOMALY_MESSAGES: Record<string, string> = {
  unusually_low: "⚠️ This estimate looks unusually low for the given surface.",
  unusually_high: "⚠️ This estimate looks unusually high for the given surface.",
};

function renderResult(container: HTMLElement, value: number, low?: number, high?: number, anomalyWarning?: string): void {
  let html = `<p><strong>Estimated value:</strong> ${Math.round(value).toLocaleString("en-GB")} €</p>`;
  if (low != null && high != null) {
    html += `<p>Range: ${Math.round(low).toLocaleString("en-GB")} – ${Math.round(high).toLocaleString("en-GB")} €</p>`;
  }
  if (anomalyWarning != null) {
    const message = ANOMALY_MESSAGES[anomalyWarning] ?? `⚠️ ${anomalyWarning}`;
    html += `<p style="color: orange">${message}</p>`;
  }
  container.innerHTML = html;
}

function renderError(container: HTMLElement, message: string): void {
  container.innerHTML = `<p style="color:red">Error: ${message}</p>`;
}

function renderLoading(container: HTMLElement): void {
  container.innerHTML = "<p>Loading…</p>";
}

export function mountDisplay(container: HTMLElement): void {
  window.addEventListener("cesar-params-change", async (e: Event) => {
    const params = (e as CustomEvent<EstimateParams>).detail;
    renderLoading(container);
    try {
      const base = getApiBase();
      const result = await fetchEstimate(base, params);
      renderResult(
        container,
        result.estimated_value_eur,
        result.value_low_eur,
        result.value_high_eur,
        result.anomaly_warning,
      );
    } catch (err) {
      renderError(container, err instanceof Error ? err.message : String(err));
    }
  });
}
