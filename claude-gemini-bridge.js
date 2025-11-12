import { execSync } from "child_process";
import fs from "fs";
import path from "path";

const promptFile = path.resolve("./gemini_prompt.txt");
const outputFile = path.resolve("./gemini_output.txt");

console.log("🧠 Claude ↔ Gemini bridge running...");
console.log("Watching:", promptFile);

fs.watchFile(promptFile, async () => {
  const prompt = fs.readFileSync(promptFile, "utf-8").trim();
  if (!prompt) return;

  console.log("\n📥 Received prompt from Claude:\n", prompt);

  try {
    const result = execSync(`gemini prompt "${prompt}"`, { encoding: "utf-8" });
    fs.writeFileSync(outputFile, result);
    console.log("\n✅ Output saved to", outputFile);
  } catch (err) {
    fs.writeFileSync(outputFile, "❌ Error: " + err.message);
    console.error(err);
  }
});
