// static/js/main.js
document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.getElementById("fileInput");
  const uploadBtn = document.getElementById("uploadBtn");
  const preview = document.getElementById("preview");
  const msg = document.getElementById("msg");
  const resultPanel = document.getElementById("resultPanel");
  const predLabel = document.getElementById("predLabel");
  const probList = document.getElementById("probList");
  const recs = document.getElementById("recs");

  let currentFile = null;

  fileInput.addEventListener("change", (e) => {
    const f = e.target.files[0];
    if (!f) return;
    currentFile = f;
    preview.src = URL.createObjectURL(f);
    preview.style.display = "block";
    resultPanel.style.display = "none";
    msg.textContent = "";
  });

  uploadBtn.addEventListener("click", async () => {
    if (!currentFile) {
      msg.textContent = "Vui lòng chọn ảnh trước khi upload.";
      return;
    }
    await uploadAndPredict(currentFile);
  });

  async function uploadAndPredict(file) {
    msg.textContent = "Đang gửi ảnh lên server...";

    const form = new FormData();
    form.append("image", file, file.name);

    try {
      const res = await fetch("/predict", { method: "POST", body: form });
      const data = await res.json();
      if (!res.ok) {
        msg.textContent = data.error || "Lỗi server";
        return;
      }
      // hiển thị image từ server (đường dẫn)
      preview.src = data.image_url;
      preview.style.display = "block";

      predLabel.textContent = data.pred_label;
      // probabilities
      probList.innerHTML = "";
      const probs = data.probabilities;
      for (const k of Object.keys(probs)) {
        const p = Math.round(probs[k]*10000)/100; // 2 chữ số thập phân
        const div = document.createElement("div");
        div.textContent = `${k}: ${p}%`;
        probList.appendChild(div);
      }
      // recommendations
      recs.innerHTML = "";
      data.recommendations.forEach(r => {
        const li = document.createElement("li");
        li.textContent = r;
        recs.appendChild(li);
      });

      resultPanel.style.display = "block";
      msg.textContent = "Dự báo hoàn tất.";
    } catch (err) {
      console.error(err);
      msg.textContent = "Lỗi khi kết nối server.";
    }
  }

  // ---------- Camera capture ----------
  const video = document.getElementById("video");
  const canvas = document.getElementById("canvas");
  const snapBtn = document.getElementById("snapBtn");

  // mở camera
  async function startCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      video.srcObject = stream;
    } catch (err) {
      console.error("Không thể mở camera:", err);
    }
  }

  startCamera();

  snapBtn.addEventListener("click", async () => {
    // vẽ video lên canvas rồi chuyển thành blob
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(async (blob) => {
      if (!blob) return;
      // tạo file tạm
      const file = new File([blob], "capture.jpg", { type: "image/jpeg" });
      preview.src = URL.createObjectURL(file);
      preview.style.display = "block";
      await uploadAndPredict(file);
    }, "image/jpeg", 0.95);
  });
});
