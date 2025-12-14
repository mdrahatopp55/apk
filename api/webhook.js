const GH_API = "https://api.github.com";

export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(200).send("OK");

  const body = req.body;
  const msg = body.message;
  if (!msg) return res.end();

  const { BOT_TOKEN, GH_TOKEN, GH_REPO, ADMIN_ID } = process.env;
  const BRANCH = "main";

  const chatId = msg.chat?.id;
  const userId = msg.from?.id;
  if (!chatId) return res.end();

  // ================= SEND MESSAGE =================
  const send = async (text, keyboard = null) => {
    const payload = {
      chat_id: chatId,
      text,
      parse_mode: "HTML"
    };
    if (keyboard) payload.reply_markup = keyboard;

    await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
  };

  // ================= ADMIN CHECK =================
  if (String(userId) !== String(ADMIN_ID)) {
    await send("⛔ <b>Admin only</b>");
    return res.end();
  }

  // ================= KEYBOARDS =================
  const mainKeyboard = {
    keyboard: [
      ["📤 Upload File"],
      ["📂 List Files", "🧾 Logs"],
      ["🗑 Delete", "✏️ Rename"]
    ],
    resize_keyboard: true
  };

  const ghHeaders = {
    "Authorization": `token ${GH_TOKEN}`,
    "Content-Type": "application/json"
  };

  // ================= LOG SYSTEM =================
  async function log(action, file) {
    const path = "logs/uploads.json";
    let logs = [], sha = null;

    const r = await fetch(`${GH_API}/repos/${GH_REPO}/contents/${path}`, {
      headers: ghHeaders
    });

    if (r.status === 200) {
      const j = await r.json();
      sha = j.sha;
      logs = JSON.parse(Buffer.from(j.content, "base64").toString());
    }

    logs.unshift({ action, file, time: new Date().toISOString() });
    logs = logs.slice(0, 50);

    await fetch(`${GH_API}/repos/${GH_REPO}/contents/${path}`, {
      method: "PUT",
      headers: ghHeaders,
      body: JSON.stringify({
        message: "update logs",
        content: Buffer.from(JSON.stringify(logs, null, 2)).toString("base64"),
        sha,
        branch: BRANCH
      })
    });
  }

  // ================= COMMAND HANDLER =================
  const text = msg.text;

  if (text === "/start") {
    await send(
`🤖 <b>GitHub File Host Bot</b>

📤 Send file → upload to GitHub
📂 List uploaded files
🧾 View logs
🗑 Delete file
✏️ Rename file`,
      mainKeyboard
    );
    return res.end();
  }

  if (text === "📂 List Files") {
    const r = await fetch(`${GH_API}/repos/${GH_REPO}/contents/uploads`, { headers: ghHeaders });
    if (r.status !== 200) {
      await send("📭 No files found", mainKeyboard);
      return res.end();
    }
    const j = await r.json();
    await send("📂 <b>Files</b>\n\n" + j.map(f => `• ${f.name}`).join("\n"), mainKeyboard);
    return res.end();
  }

  if (text === "🧾 Logs") {
    const r = await fetch(`${GH_API}/repos/${GH_REPO}/contents/logs/uploads.json`, { headers: ghHeaders });
    if (r.status !== 200) {
      await send("🧾 No logs yet", mainKeyboard);
      return res.end();
    }
    const j = await r.json();
    const logs = JSON.parse(Buffer.from(j.content, "base64").toString());
    await send(
      "🧾 <b>Last Logs</b>\n\n" +
      logs.slice(0, 10).map(l => `• ${l.action} → ${l.file}`).join("\n"),
      mainKeyboard
    );
    return res.end();
  }

  // ================= FILE UPLOAD =================
  const file =
    msg.document ??
    msg.video ??
    msg.audio ??
    (Array.isArray(msg.photo) ? msg.photo.at(-1) : null);

  if (!file?.file_id) {
    await send("📤 Please send a file", mainKeyboard);
    return res.end();
  }

  // ================= GET FILE FROM TELEGRAM =================
  const fInfo = await fetch(
    `https://api.telegram.org/bot${BOT_TOKEN}/getFile?file_id=${file.file_id}`
  ).then(r => r.json());

  if (!fInfo.ok || !fInfo.result?.file_path) {
    console.log("Telegram getFile error:", fInfo);
    await send("❌ Failed to fetch file from Telegram", mainKeyboard);
    return res.end();
  }

  const filePath = fInfo.result.file_path;
  const fileUrl = `https://api.telegram.org/file/bot${BOT_TOKEN}/${filePath}`;
  const buffer = await fetch(fileUrl).then(r => r.arrayBuffer());
  const base64 = Buffer.from(buffer).toString("base64");

  const name = `uploads/${Date.now()}_${filePath.split("/").pop()}`;

  // ================= UPLOAD TO GITHUB =================
  await fetch(`${GH_API}/repos/${GH_REPO}/contents/${name}`, {
    method: "PUT",
    headers: ghHeaders,
    body: JSON.stringify({
      message: "upload",
      content: base64,
      branch: BRANCH
    })
  });

  await log("UPLOAD", name);

  const raw = `https://raw.githubusercontent.com/${GH_REPO}/${BRANCH}/${name}`;
  await send(`✅ <b>Uploaded Successfully</b>\n\n🔗 ${raw}`, mainKeyboard);

  res.end();
}
