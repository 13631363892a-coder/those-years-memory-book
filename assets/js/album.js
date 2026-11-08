/* ============================================================
   那些年，我们一起走过 — 相册运行时
   翻页核心沿用 create-photo-flipbook-ui / ui-collections/2d-book
   的 St.PageFlip 初始化参数与左右页书脊阴影处理；
   在其之上扩展：章节导航、目录跳转、页码、全屏、灯箱、
   分级图片懒加载、背景音乐开关。
   ============================================================ */
(function () {
  "use strict";

  var CFG = window.ALBUM;
  var IDX = window.PHOTO_INDEX || {};
  if (!CFG) { console.error("content.js 未加载"); return; }

  var PW = 560, PH = 760;
  var $ = function (s) { return document.querySelector(s); };
  var esc = function (s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  };
  var pad = function (n) { return String(n).padStart(2, "0"); };

  /* ---------- 照片 ---------- */
  function meta(id) { return IDX[id] || {}; }
  function dateOf(id) {
    var d = meta(id).dt;
    if (!d || d.length < 10) return "";
    return d.slice(0, 10).replace(/:/g, ".");
  }
  function dateLine(id) {
    var d = dateOf(id);
    return d ? "拍摄于 " + d : "";
  }
  /* 统一图片标签：thumb 先加载，放大时才取 full */
  function img(id, cls, cap) {
    if (!id) return '<div class="ph ph-empty"></div>';
    return '<img class="' + (cls || "photo-img") + '" data-id="' + esc(id) + '"' +
      ' data-cap="' + esc(cap || "") + '"' +
      ' data-src="photos/thumb/' + esc(id) + '.webp"' +
      ' alt="照片' + (dateOf(id) ? "，拍摄于 " + dateOf(id) : "") + '"' +
      ' loading="lazy" decoding="async">';
  }
  function ph(id, cls, cap) {
    return '<div class="ph">' + img(id, cls || "", cap) + "</div>";
  }

  var INTERLUDES = [
    "有些日子，当时只道是寻常。",
    "下课铃响之前，时间过得很慢。",
    "窗外的树，又长高了一点。",
    "照片会泛黄，那天不会。",
    "我们没有告别，只是各自走出了校门。",
    "很多年后才明白，那是最好走的一段路。",
    "走廊很长，课间很短。",
    "风把窗帘吹起来的时候，夏天就到了。",
    "记得的不多，但都还记得。",
    "后来再没有那样的一整个下午。"
  ];

  /* ---------- 单页渲染 ---------- */
  function render(spec, index, ctx) {
    var t = spec.t, body = "", cls = "page", density = "", chapter = ctx.chapter;
    var folio = '<span class="folio ' + (index % 2 === 1 ? "left" : "right") + '">' + pad(index + 1) + "</span>";
    var head = ctx.chapterTitle
      ? '<span class="running-head ' + (index % 2 === 1 ? "left" : "right") + '">' + esc(ctx.chapterTitle) + "</span>"
      : "";
    var dark = false;

    switch (t) {
      case "cover":
        cls += " p-cover"; density = ' data-density="hard"'; dark = true;
        body =
          '<div class="cover-frame"></div><div class="cover-inner">' +
          '<div class="cover-eyebrow">' + esc(CFG.meta.years || "初二 — 初三") + "</div>" +
          '<div class="cover-rule"></div>' +
          '<h1 class="cover-title">' + esc(CFG.meta.titleLine1) + "<br>" + esc(CFG.meta.titleLine2) + "</h1>" +
          '<p class="cover-sub">' + esc(CFG.meta.subtitle) + "</p>" +
          (spec.photo
            ? '<div class="cover-photo">' + img(spec.photo, "", "") +
              '<span class="cap">' + esc(spec.photoCap || "") + "</span></div>"
            : "") +
          '<div class="cover-foot">' + esc(CFG.meta.foot || "2024 — 2026") + "</div>" +
          '<div class="cover-open" id="cover-open">轻点翻开 →</div>' +
          "</div>";
        break;

      case "endpaper":
        cls += " p-endpaper";
        body = '<div class="endpaper-mark">' + esc(spec.text || "谨以此册，留住那两年") + "</div>";
        break;

      case "endpaperBack":
        cls += " p-endpaper back";
        body = '<div class="endpaper-mark">' + esc(spec.text || "故事没有结束") + "</div>";
        break;

      case "title":
        cls += " p-title";
        body =
          '<p class="title-kicker">A MEMORY BOOK · 青春纪念册</p>' +
          '<h2 class="title-main">' + esc(spec.title || CFG.meta.titleLine1 + "<br>" + CFG.meta.titleLine2).replace(/&lt;br&gt;/g, "<br>") + "</h2>" +
          '<div class="title-line"></div>' +
          '<p class="title-note">' + esc(spec.text || "").replace(/\n/g, "<br>") + "</p>" +
          '<div class="title-year">' + esc(CFG.meta.years) + " · " + esc(CFG.meta.foot) + "</div>";
        break;

      case "toc":
        cls += " p-toc";
        var items = CFG.chapters.map(function (ch) {
          var pg = ctx.chapterStart[ch.id] != null ? pad(ctx.chapterStart[ch.id] + 1) : "—";
          return '<button class="toc-item" type="button" data-goto="' + esc(ch.id) + '">' +
            '<span class="toc-no">' + esc(ch.no) + "</span>" +
            '<span class="toc-name">' + esc(ch.title) + "<small>" + esc(ch.sub || "") + "</small></span>" +
            '<span class="toc-pg">' + pg + "</span></button>";
        }).join("");
        body = '<h2 class="toc-head">目 录</h2><p class="toc-sub">CONTENTS</p>' +
          '<nav class="toc-list">' + items + "</nav>" +
          '<p class="toc-foot">' + esc(spec.note || "从初二到初三，一页一页，慢慢翻。") + "</p>";
        break;

      case "prologue":
        cls += " p-prologue";
        body = '<div class="prologue-label">' + esc(spec.label || "序") + "</div>" +
          '<p class="prologue-text">' + esc(spec.text || "").replace(/\n/g, "<br>") + "</p>" +
          '<div class="prologue-sign">' + esc(spec.sign || "") + "</div>";
        break;

      case "chapter":
        var chSpec = (CFG.chapters || []).filter(function (x) { return x.id === spec.id; })[0] || {};
        cls += " p-chapter " + (spec.tone || "tone-1");
        chapter = spec.id;
        body = '<div class="chapter-top">' +
            '<div class="chapter-no">' + esc(spec.no || chSpec.no || "") + "</div>" +
            '<div class="chapter-rule"></div>' +
            '<h2 class="chapter-title">' + esc(spec.title || chSpec.title || "") + "</h2>" +
            '<p class="chapter-sub">' + esc(spec.sub || chSpec.sub || "") + "</p>" +
            '<p class="chapter-intro">' + esc(spec.intro || chSpec.intro || "").replace(/\n/g, "<br>") + "</p>" +
          "</div>" +
          (spec.photo ? '<div class="chapter-visual">' +
              '<div class="chapter-photo">' + ph(spec.photo) + "</div>" +
              '<p class="chapter-photo-cap">' + (dateOf(spec.photo) ? "拍摄于 " + dateOf(spec.photo) : "") + "</p>" +
            "</div>" : "") +
          '<div class="chapter-bottom">' + esc(chSpec.sub || "") + "</div>";
        break;

      /* 图文错落：文字在左上、大图偏右、小照片斜放在左下 */
      case "story":
        cls += " p-story";
        var sps = spec.photos || [];
        body = '<p class="story-kicker">' + esc(spec.kicker || "") + "</p>" +
          '<h3 class="story-head">' + esc(spec.head || "") + "</h3>" +
          '<p class="story-text">' + esc(spec.text || "").replace(/\n/g, "<br>") + "</p>" +
          '<div class="story-main">' + (sps[0] ? ph(sps[0].id, "", sps[0].cap) : "") + "</div>" +
          '<div class="story-sub">' + (sps[1] ? ph(sps[1].id, "", sps[1].cap) : "") +
            (sps[1] && sps[1].cap ? '<span class="story-sub-cap">' + esc(sps[1].cap) + "</span>" : "") + "</div>" +
          '<p class="story-foot">' + esc(spec.foot || "") + "</p>";
        break;

      /* 短句 + 一张小照片，替代纯文字页，让每一页都有图 */
      case "note":
        cls += " p-note";
        body = '<div class="note-quote"><span class="quote-mark">“</span>' +
            '<p>' + esc(spec.text || "").replace(/\n/g, "<br>") + "</p></div>" +
          (spec.photo ? '<div class="note-photo">' + ph(spec.photo) + "</div>" : "") +
          '<p class="note-meta">' + esc(spec.meta || "") + "</p>";
        break;

      case "full":
        // 横幅照片不铺满竖版页（会裁掉大半），改为完整呈现 + 纸面留白
        cls += " p-full" + ((meta(spec.photo).ratio || 1) > 1.25 ? " wide" : "");
        dark = (meta(spec.photo).ratio || 1) <= 1.25;
        body = ph(spec.photo, "", spec.cap) +
          '<div class="photo-shade"></div>' +
          (spec.cap ? '<div class="full-caption">' + esc(spec.cap).replace(/\n/g, "<br>") + "</div>" : "") +
          (spec.showDate !== false ? '<div class="full-meta">' + esc(dateLine(spec.photo)) + "</div>" : "");
        break;

      case "spreadL":
      case "spreadR":
        cls += " p-spread " + (t === "spreadL" ? "spread-l" : "spread-r"); dark = true;
        body = ph(spec.photo, "", spec.cap) +
          ((t === "spreadL" ? spec.noteL : spec.noteR)
            ? '<div class="spread-note">' + esc(t === "spreadL" ? spec.noteL : spec.noteR) + "</div>" : "");
        break;

      case "frame":
        cls += " p-frame";
        body = '<div class="frame-top"><span>' + esc(spec.top || "") + "</span><span>" +
          esc(spec.showDate === false ? "" : dateOf(spec.photo)) + "</span></div>" +
          '<div class="polaroid" style="transform:rotate(' + (spec.rotate == null ? -1.4 : spec.rotate) + 'deg)">' +
          '<span class="tape tl"></span>' + ph(spec.photo, "", spec.written) +
          (spec.written ? '<div class="handwritten">' + esc(spec.written) + "</div>" : "") + "</div>" +
          (spec.quote ? '<p class="frame-quote">' + esc(spec.quote).replace(/\n/g, "<br>") + "</p>" : "") +
          '<div class="frame-meta">' + esc(spec.meta || dateLine(spec.photo)) + "</div>";
        break;

      case "duo":
        cls += " p-duo " + (spec.orient === "horizontal" ? "horizontal" : "vertical");
        var ditems = (spec.photos || []).map(function (p) {
          return '<div class="duo-item">' + ph(p.id, "", p.cap) +
            (p.cap ? '<div class="cap">' + esc(p.cap) + "</div>" : "") + "</div>";
        }).join("");
        body = (spec.head ? '<div class="duo-head">' + esc(spec.head) + "</div>" : "") +
          '<div class="duo-grid">' + ditems + "</div>" +
          '<div class="duo-foot">' + esc(spec.foot || "") + "</div>";
        break;

      case "collage":
        cls += " p-collage";
        var cards = (spec.photos || []).map(function (p) {
          return '<div class="collage-card"><span class="tape tl"></span>' + ph(p.id, "", p.cap) +
            (p.cap ? '<div class="cc">' + esc(p.cap) + "</div>" : "") + "</div>";
        }).join("");
        body = '<h3 class="collage-title">' + esc(spec.title || "") + "</h3>" +
          '<p class="collage-sub">' + esc(spec.sub || "") + "</p>" +
          '<div class="collage-area">' + cards + "</div>";
        break;

      case "timeline":
        cls += " p-timeline";
        var tl = (spec.items || []).map(function (it) {
          // 日期只取真实 EXIF 日期；没有 EXIF 时留空，绝不编造
          var real = it.date === "auto" || it.date == null ? dateOf(it.id) : "";
          return '<div class="tl-item"><div class="tl-photo">' + img(it.id, "", it.text) + "</div>" +
            '<div><div class="tl-date">' + esc(real) + "</div>" +
            '<div class="tl-text">' + esc(it.text || "") + "</div></div></div>";
        }).join("");
        body = '<h3 class="timeline-head">' + esc(spec.head || "") + "</h3>" +
          '<p class="timeline-sub">' + esc(spec.sub || "") + "</p>" +
          '<div class="timeline-list">' + tl + "</div>";
        break;

      case "quote":
        cls += " p-quote";
        body = '<div class="quote-mark">“</div>' +
          '<p class="quote-text">' + esc(spec.text || "").replace(/\n/g, "<br>") + "</p>" +
          (spec.note ? '<div class="quote-note">' + esc(spec.note) + "</div>" : "");
        break;

      case "interlude":
        cls += " p-quote";
        body = '<div class="quote-mark">“</div>' +
          '<p class="quote-text">' + esc(INTERLUDES[(spec.i || 0) % INTERLUDES.length]) + "</p>";
        break;

      case "letter":
        cls += " p-letter";
        var paras = (spec.paras || []).map(function (p) { return "<p>" + esc(p).replace(/\n/g, "<br>") + "</p>"; }).join("");
        body = '<p class="letter-head">' + esc(spec.head || "写给过去的自己：") + "</p>" +
          '<div class="letter-body">' + paras + "</div>" +
          '<div class="letter-sign">' + esc(spec.sign || "") + "</div>" +
          '<div class="letter-seal">念</div>';
        break;

      case "backcover":
        cls += " p-backcover"; density = ' data-density="hard"'; dark = true;
        body = '<div class="cover-frame"></div><div class="backcover-note">' +
          '<div class="seal">念</div><p>' + esc(spec.text || "故事没有结束") + "</p>" +
          '<p style="font-family:var(--sans);font-size:10px;letter-spacing:.3em;opacity:.7">' +
          esc(CFG.meta.foot || "2024 — 2026") + "</p></div>";
        break;

      default:
        cls += " p-quote";
        body = '<p class="quote-text">' + esc(spec.text || "") + "</p>";
    }

    var folioHtml = (t === "cover" || t === "backcover" || t === "endpaper" || t === "endpaperBack")
      ? "" : folio;
    if (dark) folioHtml = folioHtml.replace('class="folio ', 'class="folio on-dark ');
    return '<article class="' + cls + '"' + density +
      (t === "spreadL" || t === "spreadR" ? ' data-spread="1"' : '') +
      ' data-chapter="' + esc(chapter || "") + '"' +
      ' data-index="' + index + '">' + body +
      '<div class="paper-grain"></div>' + head + folioHtml + "</article>";
  }

  /* ---------- 展开跨页、补齐偶数页 ---------- */
  function normalize(specs) {
    var flat = [], inter = 0;
    specs.forEach(function (s) {
      if (s.t === "spread") {
        // StPageFlip(showCover) 的跨页配对为 (1,2),(3,4)…；spread 左半须落在奇数下标
        if (flat.length % 2 === 0) flat.push({ t: "interlude", i: inter++ });
        flat.push(Object.assign({}, s, { t: "spreadL" }));
        flat.push(Object.assign({}, s, { t: "spreadR" }));
      } else {
        flat.push(s);
      }
    });
    if (flat.length % 2 === 1) flat.splice(flat.length - 1, 0, { t: "interlude", i: inter++ });
    return flat;
  }

  /* ---------- 构建页面 ---------- */
  var book = $("#book");
  var specs = normalize(CFG.pages);
  var chapterStart = {}, chapterTitle = {}, chapterOrder = [];
  var currentCh = "", currentTitle = CFG.meta.coverChapter || "致那段回不去的时光";

  // 先扫一遍记录章节起始页
  specs.forEach(function (s, i) {
    if (s.t === "chapter") {
      chapterStart[s.id] = i;
      var c = CFG.chapters.filter(function (x) { return x.id === s.id; })[0];
      chapterTitle[s.id] = c ? c.title : s.title;
      chapterOrder.push(s.id);
    }
  });

  var html = "";
  specs.forEach(function (s, i) {
    if (s.t === "chapter") { currentCh = s.id; }
    var ctx = { chapter: currentCh, chapterTitle: chapterTitle[currentCh] || "", chapterStart: chapterStart };
    html += render(s, i, ctx);
  });
  book.innerHTML = html;
  var pageEls = Array.prototype.slice.call(book.querySelectorAll(".page"));

  /* StPageFlip 的 size:"stretch" 会直接改写 .page 的 CSS 宽高（窄屏单页时
     只有 374px），而版式是按 560×760 设计的。把版式类与内容移进一层固定
     尺寸的画布，再按实际页宽等比缩放，桌面/手机排版就完全一致了。
     data-density / data-chapter / data-index 必须留在 .page 上。 */
  pageEls.forEach(function (pg) {
    var canvas = document.createElement("div");
    canvas.className = "page-canvas";
    Array.prototype.slice.call(pg.classList).forEach(function (c) {
      if (c !== "page" && c.indexOf("stf__") !== 0) {
        pg.classList.remove(c);
        canvas.classList.add(c);
      }
    });
    while (pg.firstChild) canvas.appendChild(pg.firstChild);
    pg.appendChild(canvas);
  });

  /* 图片入场动效：按页内顺序错开浮现，翻到该页时触发 */
  document.documentElement.classList.add("js-reveal");
  pageEls.forEach(function (pg) {
    var nodes = pg.querySelectorAll(".ph");
    for (var i = 0; i < nodes.length; i++) {
      nodes[i].classList.add("reveal");
      nodes[i].style.setProperty("--d", (i * 105) + "ms");
    }
  });
  function activateVisible() {
    for (var i = 0; i < pageEls.length; i++) pageEls[i].classList.remove("is-active");
    void book.offsetWidth; // 强制重排，保证重新播放动画
    if (pageEls[currentPage]) pageEls[currentPage].classList.add("is-active");
    if (pageEls[currentPage + 1]) pageEls[currentPage + 1].classList.add("is-active");
  }

  // 每章的显示名（用于状态栏）
  function chapterNameAt(idx) {
    // 双页模式下当前显示 idx / idx+1 两页；章首页可能落在右页，
    // 因此取两页中章节顺序更靠后的那个，避免状态栏滞后一章。
    var found = "";
    for (var j = idx; j <= Math.min(idx + 1, pageEls.length - 1); j++) {
      var c = pageEls[j] && pageEls[j].getAttribute("data-chapter");
      if (c && (!found || chapterOrder.indexOf(c) > chapterOrder.indexOf(found))) found = c;
    }
    if (!found) {
      for (var i = idx - 1; i >= 0; i--) {
        var c2 = pageEls[i] && pageEls[i].getAttribute("data-chapter");
        if (c2) { found = c2; break; }
      }
    }
    if (!found) {
      var first = chapterStart[chapterOrder[0]];
      return (first == null || idx <= first) ? (CFG.meta.coverChapter || "封面") : "故事没有结束";
    }
    var ch = CFG.chapters.filter(function (x) { return x.id === found; })[0];
    return ch ? ch.title : found;
  }

  /* ---------- 翻页运行时（沿用原项目参数） ---------- */
  var pageFlip = new St.PageFlip(book, {
    width: PW,
    height: PH,
    size: "stretch",
    minWidth: Math.max(1, Math.round(PW * 0.5)),
    maxWidth: Math.max(1, Math.round(PW * 1.08)),
    minHeight: Math.max(1, Math.round(PH * 0.5)),
    maxHeight: Math.max(1, Math.round(PH * 1.08)),
    drawShadow: true,
    flippingTime: 820,
    usePortrait: true,
    startZIndex: 10,
    autoSize: true,
    maxShadowOpacity: 0.4,
    showCover: true,
    mobileScrollSupport: false,
    clickEventForward: true,
    useMouseEvents: true,
    swipeDistance: 24,
    showPageCorners: true,
    disableFlipByClick: false
  });

  /* 实际页宽 / 设计页宽 → 版式画布的缩放比 */
  function updateScale() {
    var pw = 0;
    for (var i = 0; i < pageEls.length; i++) {
      var w = pageEls[i].getBoundingClientRect().width;
      if (w > 10) { pw = w; break; }
    }
    if (!pw) {
      var bw = book.getBoundingClientRect().width;
      pw = bw > 0 ? bw : PW;
    }
    document.documentElement.style.setProperty("--s", (pw / PW).toFixed(5));
  }

  var currentPage = 0, isTurning = false;
  var previous = $("#previous"), next = $("#next");
  var pageStatus = $("#page-status"), chapterNameEl = $("#chapter-name"), chapterNote = $("#chapter-note");

  function loadNearby(center) {
    var lo = Math.max(0, center - 4), hi = Math.min(pageEls.length, center + 6);
    for (var i = lo; i < hi; i++) {
      var imgs = pageEls[i].querySelectorAll("img[data-src]");
      for (var j = 0; j < imgs.length; j++) {
        var im = imgs[j];
        im.src = im.dataset.src;
        im.removeAttribute("data-src");
      }
    }
  }

  function updateControls() {
    var n = pageFlip.getPageCount();
    previous.disabled = currentPage === 0 || isTurning;
    next.disabled = currentPage >= n - 1 || isTurning;
    if (currentPage === 0) pageStatus.textContent = "封面";
    else if (currentPage >= n - 1) pageStatus.textContent = "封底";
    else pageStatus.textContent = pad(currentPage + 1) + " / " + pad(n);
    var nm = chapterNameAt(currentPage);
    chapterNameEl.textContent = nm;
    chapterNote.textContent = nm;
    loadNearby(currentPage);
  }

  pageFlip.on("flip", function (e) { currentPage = Number(e.data); updateControls(); activateVisible(); });
  pageFlip.on("changeState", function (e) { isTurning = e.data !== "read"; updateControls(); });
  pageFlip.on("init", function () { updateScale(); updateControls(); loadNearby(0); activateVisible(); });
  pageFlip.on("changeOrientation", function () { updateScale(); activateVisible(); });
  pageFlip.loadFromHTML(pageEls);
  updateScale();
  updateControls();
  loadNearby(0);
  activateVisible();
  setTimeout(function () { $("#loading").classList.add("hide"); }, 460);

  function goNext() { if (!isTurning) pageFlip.flipNext("bottom"); }
  function goPrev() { if (!isTurning) pageFlip.flipPrev("bottom"); }
  function gotoChapter(id) {
    var i = chapterStart[id];
    if (i == null) return;
    if (!isTurning) pageFlip.turnToPage(i);
    closeDrawer();
  }

  previous.addEventListener("click", goPrev);
  next.addEventListener("click", goNext);
  $("#first").addEventListener("click", function () { if (!isTurning) pageFlip.turnToPage(0); });
  $("#last").addEventListener("click", function () { if (!isTurning) pageFlip.turnToPage(pageFlip.getPageCount() - 1); });
  book.addEventListener("click", function (e) {
    if (e.target.closest("#cover-open")) { e.stopPropagation(); goNext(); }
    var to = e.target.closest("[data-goto]");
    if (to) { e.stopPropagation(); gotoChapter(to.getAttribute("data-goto")); }
  });

  /* ---------- 目录抽屉 ---------- */
  var drawer = $("#drawer");
  function closeDrawer() { drawer.classList.remove("open"); }
  $("#btn-toc").addEventListener("click", function () { drawer.classList.toggle("open"); });
  $("#drawer-close").addEventListener("click", closeDrawer);
  var drawerList = $("#drawer-list");
  drawerList.innerHTML = '<button class="drawer-item" type="button" data-goto-page="0">' +
    '<span class="no">·</span><span class="nm">封面<span class="pg">回到最初</span></span></button>' +
    CFG.chapters.map(function (ch) {
      return '<button class="drawer-item" type="button" data-goto="' + esc(ch.id) + '">' +
        '<span class="no">' + esc(ch.no) + '</span><span class="nm">' + esc(ch.title) +
        '<span class="pg">' + (chapterStart[ch.id] != null ? "第 " + pad(chapterStart[ch.id] + 1) + " 页" : "") +
        "</span></span></button>";
    }).join("");
  drawerList.addEventListener("click", function (e) {
    var b = e.target.closest("[data-goto]");
    if (b) { gotoChapter(b.getAttribute("data-goto")); return; }
    var p = e.target.closest("[data-goto-page]");
    if (p) { if (!isTurning) pageFlip.turnToPage(Number(p.getAttribute("data-goto-page"))); closeDrawer(); }
  });

  /* ---------- 灯箱 ---------- */
  var lightbox = $("#lightbox"), lbImg = $("#lb-img"), lbCap = $("#lb-cap"), lbMeta = $("#lb-meta");
  var gallery = Array.prototype.slice.call(book.querySelectorAll("img[data-id]"));
  var lbIndex = 0;
  function showLb(i) {
    lbIndex = (i + gallery.length) % gallery.length;
    var node = gallery[lbIndex], id = node.getAttribute("data-id");
    lbImg.src = "photos/full/" + id + ".jpg";
    lbImg.onerror = function () { this.onerror = null; this.src = "photos/thumb/" + id + ".webp"; };
    lbCap.textContent = node.getAttribute("data-cap") || "";
    lbMeta.textContent = dateLine(id) || "那些年，我们一起走过";
    lightbox.classList.add("open");
  }
  function closeLb() { lightbox.classList.remove("open"); lbImg.removeAttribute("src"); }
  book.addEventListener("click", function (e) {
    var im = e.target.closest("img[data-id]");
    if (!im) return;
    // 拖动翻页时不误触
    if (isTurning) return;
    var i = gallery.indexOf(im);
    if (i >= 0) { e.stopPropagation(); showLb(i); }
  });
  $("#lb-close").addEventListener("click", closeLb);
  $("#lb-prev").addEventListener("click", function (e) { e.stopPropagation(); showLb(lbIndex - 1); });
  $("#lb-next").addEventListener("click", function (e) { e.stopPropagation(); showLb(lbIndex + 1); });
  lightbox.addEventListener("click", function (e) { if (e.target === lightbox || e.target.classList.contains("lb-stage")) closeLb(); });

  /* ---------- 全屏 ---------- */
  var fsBtn = $("#btn-fullscreen");
  function toggleFs() {
    try {
      if (!document.fullscreenElement) {
        var el = document.documentElement;
        var p = el.requestFullscreen && el.requestFullscreen();
        if (p && p.catch) p.catch(function () {}); // 无头/受限环境会拒绝
      } else if (document.exitFullscreen) {
        var q = document.exitFullscreen();
        if (q && q.catch) q.catch(function () {});
      }
    } catch (e) { /* 全屏不可用时静默降级 */ }
  }
  fsBtn.addEventListener("click", toggleFs);
  document.addEventListener("fullscreenchange", function () {
    fsBtn.setAttribute("aria-pressed", document.fullscreenElement ? "true" : "false");
  });

  /* ---------- 背景音乐（默认关闭，不自动播放） ---------- */
  var musicBtn = $("#btn-music");
  var audio = null, actx = null, master = null, chordTimer = null, musicOn = false;
  var CHORDS = [[130.81, 164.81, 196.00], [110.00, 130.81, 164.81],
                [146.83, 174.61, 220.00], [98.00, 123.47, 146.83]];
  function ensureContext() {
    if (actx) return actx;
    var AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return null;
    actx = new AC();
    return actx;
  }
  function startSynth() {
    if (!ensureContext()) return false;
    if (actx.state === "suspended") {
      try { var rp = actx.resume(); if (rp && rp.catch) rp.catch(function () {}); } catch (e) {}
    }
    master = actx.createGain();
    master.gain.value = 0;
    var lp = actx.createBiquadFilter();
    lp.type = "lowpass"; lp.frequency.value = 900;
    master.connect(lp); lp.connect(actx.destination);
    master.gain.linearRampToValueAtTime(0.075, actx.currentTime + 2.2);
    var ci = 0;
    function chord() {
      var now = actx.currentTime;
      CHORDS[ci % CHORDS.length].forEach(function (f) {
        var o = actx.createOscillator(), g = actx.createGain();
        o.type = "sine"; o.frequency.value = f;
        o.detune.value = (Math.random() - .5) * 5;
        g.gain.setValueAtTime(0, now);
        g.gain.linearRampToValueAtTime(0.16, now + 1.7);
        g.gain.linearRampToValueAtTime(0, now + 6.6);
        o.connect(g); g.connect(master);
        o.start(now); o.stop(now + 6.8);
      });
      ci++;
    }
    chord();
    chordTimer = setInterval(chord, 5400);
    return true;
  }
  function musicStart() {
    // 内置的是 Web Audio 柔和和弦，完全本地、无外部请求。
    // 若想换成自己的音乐：在 content.js 里给 ALBUM 加 musicFile:"assets/audio/bgm.mp3"。
    if (CFG.musicFile) {
      audio = new Audio(CFG.musicFile);
      audio.loop = true;
      audio.volume = 0.32;
      var pr = audio.play();
      if (pr && pr.catch) pr.catch(function () { audio = null; startSynth(); });
    } else {
      startSynth(); // 同步调用，确保处于用户手势内
    }
  }
  function musicStop() {
    if (audio) { audio.pause(); audio.currentTime = 0; }
    if (chordTimer) { clearInterval(chordTimer); chordTimer = null; }
    if (master && actx) {
      try { master.gain.linearRampToValueAtTime(0, actx.currentTime + .4); } catch (e) {}
      var a = actx;
      setTimeout(function () {
        try { var cp = a.close(); if (cp && cp.catch) cp.catch(function () {}); } catch (e) {}
      }, 600);
      actx = null; master = null;
    }
  }
  function syncMusic() {
    musicBtn.setAttribute("aria-pressed", musicOn ? "true" : "false");
    musicBtn.title = musicOn ? "关闭背景音乐 (M)" : "开启背景音乐 (M)";
  }
  musicBtn.addEventListener("click", function () {
    musicOn = !musicOn;
    if (musicOn) musicStart(); else musicStop();
    syncMusic();
  });
  syncMusic();

  /* ---------- 键盘 ---------- */
  window.addEventListener("keydown", function (e) {
    if (e.altKey || e.ctrlKey || e.metaKey) return;
    if (lightbox.classList.contains("open")) {
      if (e.key === "Escape") closeLb();
      else if (e.key === "ArrowLeft") showLb(lbIndex - 1);
      else if (e.key === "ArrowRight") showLb(lbIndex + 1);
      return;
    }
    if (e.key === "Escape") { closeDrawer(); return; }
    if (e.key === "ArrowLeft" || e.key === "PageUp") { e.preventDefault(); goPrev(); }
    else if (e.key === "ArrowRight" || e.key === " " || e.key === "PageDown") { e.preventDefault(); goNext(); }
    else if (e.key === "Home") { if (!isTurning) pageFlip.turnToPage(0); }
    else if (e.key === "End") { if (!isTurning) pageFlip.turnToPage(pageFlip.getPageCount() - 1); }
    else if (e.key === "f" || e.key === "F") toggleFs();
    else if (e.key === "m" || e.key === "M") musicBtn.click();
    else if (e.key === "c" || e.key === "C") drawer.classList.toggle("open");
  });

  /* ---------- 窗口尺寸变化 ---------- */
  var rz;
  window.addEventListener("resize", function () {
    clearTimeout(rz);
    rz = setTimeout(function () {
      try { pageFlip.updateFromHtml(pageEls); } catch (e) {}
      updateScale();
    }, 220);
  });

  // 便于二次开发
  window.ALBUM_APP = { flip: pageFlip, gotoChapter: gotoChapter, pages: specs, photoIndex: IDX };
})();
