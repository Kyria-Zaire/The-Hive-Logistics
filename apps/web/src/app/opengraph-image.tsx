import { ImageResponse } from "next/og";

export const runtime = "nodejs";

export const alt = "THE HIVE LOGISTICS — Convoyage automobile";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OpenGraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          background: "#0A0A0A",
          color: "#FFFFFF",
          display: "flex",
          flexDirection: "column",
          height: "100%",
          justifyContent: "center",
          padding: "80px",
          width: "100%",
        }}
      >
        <div style={{ color: "#DC2626", display: "flex", fontSize: 24, letterSpacing: "0.12em" }}>
          THE HIVE LOGISTICS
        </div>
        <div style={{ display: "flex", fontSize: 72, fontWeight: 600, marginTop: 28 }}>
          Convoyage automobile
        </div>
      </div>
    ),
    size,
  );
}