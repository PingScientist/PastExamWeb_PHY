import { chromium } from "@playwright/test";
import { mkdir, readFile, stat, writeFile } from "node:fs/promises";

const shareUrl = process.env.UMAMI_SHARE_URL?.trim();
if (!shareUrl)
  throw new Error("UMAMI_SHARE_URL was not provided after preflight.");

const targetUrl = new URL(shareUrl);
targetUrl.searchParams.set("date", "90day");

await mkdir("dist", { recursive: true });
await mkdir("dist/diagnostics", { recursive: true });

const browser = await chromium.launch();

async function saveDiagnostics(page, theme) {
  await page
    .screenshot({
      path: `dist/diagnostics/${theme}.png`,
      fullPage: true,
    })
    .catch(() => {});

  const sanitizedHtml = await page
    .evaluate(() => {
      const clone = document.documentElement.cloneNode(true);
      clone
        .querySelectorAll("script, noscript")
        .forEach((node) => node.remove());
      clone.querySelectorAll("*").forEach((node) => {
        for (const attribute of ["action", "href", "src", "value"]) {
          node.removeAttribute(attribute);
        }
      });
      return `<!doctype html>\n${clone.outerHTML}`;
    })
    .catch(() => "<!doctype html><title>Page HTML unavailable</title>");

  await writeFile(`dist/diagnostics/${theme}.html`, sanitizedHtml);
}

async function verifyPng(path) {
  const file = await stat(path);
  const signature = (await readFile(path)).subarray(0, 8).toString("hex");
  if (file.size < 1024 || signature !== "89504e470d0a1a0a") {
    throw new Error(`Screenshot validation failed for ${path}.`);
  }
  return file.size;
}

async function capture(theme, output) {
  const context = await browser.newContext({
    viewport: { width: 1600, height: 1400 },
    deviceScaleFactor: 2,
    colorScheme: theme,
  });

  await context.addInitScript(
    ({ selectedTheme }) => {
      localStorage.setItem("zen.theme", selectedTheme);
    },
    { selectedTheme: theme },
  );

  const page = await context.newPage();
  let pageErrorCount = 0;
  page.on("pageerror", () => {
    pageErrorCount += 1;
  });

  try {
    const response = await page.goto(targetUrl.toString(), {
      waitUntil: "domcontentloaded",
      timeout: 30000,
    });

    if (!response)
      throw new Error("Umami page returned no navigation response.");
    if (response.status() >= 400) {
      throw new Error(`Umami page returned HTTP ${response.status()}.`);
    }

    const finalUrl = new URL(page.url());
    const loginForm = page.locator('input[type="password"]:visible');
    if (
      finalUrl.pathname.toLowerCase().includes("login") ||
      (await loginForm.count()) > 0
    ) {
      throw new Error("Umami share page redirected to a login page.");
    }

    const chart = page.locator("canvas:visible").first();
    await chart.waitFor({ state: "visible", timeout: 30000 });
    await page.waitForTimeout(1000);

    const chartBox = await chart.boundingBox();
    if (!chartBox || chartBox.width <= 0 || chartBox.height <= 0) {
      throw new Error("Umami chart has invalid dimensions.");
    }

    const main = page.locator("main").filter({ has: chart }).first();
    if ((await main.count()) > 0 && (await main.isVisible())) {
      await main.screenshot({ path: output });
    } else {
      await page.screenshot({ path: output, fullPage: true });
    }

    const bytes = await verifyPng(output);
    console.log(
      `Saved ${theme} screenshot (${bytes} bytes); HTTP ${response.status()}; origin ${finalUrl.origin}; page errors ${pageErrorCount}.`,
    );
    return await readFile(output);
  } catch (error) {
    await saveDiagnostics(page, theme);
    throw error;
  } finally {
    await context.close();
  }
}

try {
  const light = await capture("light", "dist/umami.png");
  const dark = await capture("dark", "dist/umami-dark.png");
  if (light.equals(dark)) {
    throw new Error("Light and dark screenshots are unexpectedly identical.");
  }
} finally {
  await browser.close();
}
