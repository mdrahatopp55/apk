const GH_API = "https://api.github.com";

export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(200).send("OK");

  const {
    BOT_TOKEN,
    GH_TOKEN,
    GH_REPO,
    ADMIN_ID
  } = process.env;

  const BRANCH = "main";
  const msg = req.body.message;
  const chatId = msg?.chat?.id;
  const userId = msg?.from?.id;
  if (!chatId) return res.end();

  const send = async (text) => {
    await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chat_id: chatId, text })
    });
  };

  // 🔐 Admin only
  if (String(userId) !== String(ADMIN_ID)) {
    await send("⛔ Admin only");
    return res.end();
  }

  const ghHeaders = {
    "Authorization": `token ${GH_TOKEN}`,
    "Content-Type": "application/json"
  };

  // ===== LOG SYSTEM =====
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

    logs.unshift({
      action,
      file,
      time: new Date().toISOString()
    });

    logs = logs.slice(0, 100);

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

  // ===== COMMANDS =====

  if (msg.text === "/start") {
    await send(
`🤖 GitHub File Host Bot

📤 Send file → GitHub host
🗑 /delete path/file
✏️ /rename old new
📂 /list
🧾 /logs`
    );
    return res.end();
  }

  // /list
  if (msg.text === "/list") {
    const r = await fetch(
      `${GH_API}/repos/${GH_REPO}/contents/uploads`,
      { headers: ghHeaders }
    );
    if (r.status !== 200) {
      await send("No files");
      return res.end();
    }
    const j = await r.json();
    const out = j.map(f => f.name).join("\n");
    await send(`📂 Files:\n${out}`);
    return res.end();
  }

  // /logs
  if (msg.text === "/logs") {
    const r = await fetch(
      `${GH_API}/repos/${GH_REPO}/contents/logs/uploads.json`,
      { headers: ghHeaders }
    );
    if (r.status !== 200) {
      await send("No logs");
      return res.end();
    }
    const j = await r.json();
    const logs = JSON.parse(Buffer.from(j.content, "base64").toString());
    const out = logs.slice(0, 10)
      .map(l => `• ${l.action} → ${l.file}`)
      .join("\n");
    await send(`🧾 Logs:\n${out}`);
    return res.end();
  }

  // /delete
  if (msg.text?.startsWith("/delete ")) {
    const file = msg.text.split(" ")[1];
    const r = await fetch(
      `${GH_API}/repos/${GH_REPO}/contents/${file}`,
      { headers: ghHeaders }
    );
    if (r.status !== 200) {
      await send("❌ Not found");
      return res.end();
    }
    const j = await r.json();

    await fetch(`${GH_API}/repos/${GH_REPO}/contents/${file}`, {
      method: "DELETE",
      headers: ghHeaders,
      body: JSON.stringify({
        message: "delete",
        sha: j.sha,
        branch: BRANCH
      })
    });

    await log("DELETE", file);
    await send(`🗑 Deleted:\n${file}`);
    return res.end();
  }

  // /rename
  if (msg.text?.startsWith("/rename ")) {
    const [, oldN, newN] = msg.text.split(" ");
    const r = await fetch(
      `${GH_API}/repos/${GH_REPO}/contents/${oldN}`,
      { headers: ghHeaders }
    );
    if (r.status !== 200) {
      await send("❌ Not found");
      return res.end();
    }
    const j = await r.json();

    await fetch(`${GH_API}/repos/${GH_REPO}/contents/${newN}`, {
      method: "PUT",
      headers: ghHeaders,
      body: JSON.stringify({
        message: "rename",
        content: j.content,
        branch: BRANCH
      })
    });

    await fetch(`${GH_API}/repos/${GH_REPO}/contents/${oldN}`, {
      method: "DELETE",
      headers: ghHeaders,
      body: JSON.stringify({
        message: "remove old",
        sha: j.sha,
        branch: BRANCH
      })
    });

    await log("RENAME", `${oldN} → ${newN}`);
    await send("✏️ Renamed");
    return res.end();
  }

  // ===== UPLOAD =====
  const file =
    msg.document ||
    msg.video ||
    msg.audio ||
    msg.photo?.slice(-1)[0];

  if (!file) {
    await send("📤 Send file");
    return res.end();
  }

  const fInfo = await fetch(
    `https://api.telegram.org/bot${BOT_TOKEN}/getFile?file_id=${file.file_id}`
  ).then(r => r.json());

  const filePath = fInfo.result.file_path;
  const url = `https://api.telegram.org/file/bot${BOT_TOKEN}/${filePath}`;
  const buffer = await fetch(url).then(r => r.arrayBuffer());
  const base64 = Buffer.from(buffer).toString("base64");

  const name = `uploads/${Date.now()}_${filePath.split("/").pop()}`;

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
  await send(`✅ Uploaded\n🔗 ${raw}`);

  res.end();
}
