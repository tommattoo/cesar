import L from "leaflet";

// Public GeoJSON of French departments (simplified polygons, ~200 KB).
// Each feature has properties.code ("75", "2A", …) matching code_departement in the API.
const DEPARTMENTS_GEOJSON_URL =
  "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson";

export function mountMap(
  container: HTMLElement,
  onDepartmentClick: (code: string) => void,
): void {
  const map = L.map(container).setView([46.6, 2.4], 6);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap",
  }).addTo(map);

  fetch(DEPARTMENTS_GEOJSON_URL)
    .then((res) => res.json())
    .then((geojson) => {
      L.geoJSON(geojson, {
        style: { color: "#555", weight: 1, fillOpacity: 0.1 },
        onEachFeature(feature, layer) {
          const code: string = feature.properties?.code ?? "";
          layer.bindTooltip(code);
          layer.on("click", () => onDepartmentClick(code));
        },
      }).addTo(map);
    });
}
