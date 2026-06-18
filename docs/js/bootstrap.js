import { ensureAccess } from "./access.js";

await ensureAccess();
await import("./main.js?v=6");
