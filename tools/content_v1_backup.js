/* ============================================================
   那些年，我们一起走过 — 内容配置
   ------------------------------------------------------------
   这个文件是整本相册唯一需要手工编辑的内容文件。
   pages 数组按阅读顺序排列，每一项是一「页」；
   t:'spread' 会自动展开成左右两页（真正的跨页大图）。
   照片用 6 位短码引用，对应 photos/thumb/<短码>.webp。
   日期一律取自照片真实 EXIF（见 photo-index.js），
   没有 EXIF 的照片不会显示任何日期，也不会编造。
   ============================================================ */
window.ALBUM = {
  meta: {
    titleLine1: "那些年，",
    titleLine2: "我们一起走过",
    subtitle: "初二至初三 · 一段不会重来的青春",
    years: "初二 — 初三",
    foot: "2024 — 2026",
    coverChapter: "致那段回不去的时光"
  },

  chapters: [
    {
      id: "ch1", no: "01", title: "初二 · 故事的开始", sub: "2024 年秋 — 2025 年夏",
      intro: "刚开始的时候，谁都没想过会记得这么久。\n校运会、校庆、研学、期末的教室。\n相机里存下了许多当时没在意的一分钟。"
    },
    {
      id: "ch2", no: "02", title: "少年日常 · 镜头里的我们", sub: "散落在两年里的普通一天",
      intro: "课间十分钟，桌上摊开的练习册，\n有人忽然凑过来比了个耶。\n没有什么大事发生，只是刚好有人按下了快门。"
    },
    {
      id: "ch3", no: "03", title: "初三 · 时间开始加速", sub: "2025 年秋 — 2026 年春",
      intro: "日子忽然变得很整齐：上课、做题、考试，再上课。\n校运会那天的彩色烟雾，礼堂里翻到一半的书，\n还有操场上举起来的 2026。\n忙是真的，热闹也是真的。"
    },
    {
      id: "ch4", no: "04", title: "那些重要的人", sub: "一些没有写名字的合影",
      intro: "照片里的人，我一个名字也没写。\n不是忘了，是怕写错，也怕写少了。\n反正看到这些脸，就会想起那一整间教室。"
    },
    {
      id: "ch5", no: "05", title: "青春散场 · 毕业与告别", sub: "2026 年 7 月",
      intro: "七月二日，礼堂的灯很亮，舞台边摆着花。\n拍完合影，镜头又转向教学楼的窗、走廊和天上的云。\n后来相册里，最多的反而是这些没有人的照片。"
    },
    {
      id: "ch6", no: "06", title: "尾声 · 故事没有结束", sub: "写给过去的自己",
      intro: "写到最后一页，还是不知道该怎么收尾。\n那就先合上吧。"
    }
  ],

  pages: [
    /* ---------- 封面与开篇 ---------- */
    { t: "cover", photo: "2208a8", photoCap: "校园 · 2026.07.02" },
    { t: "endpaper", text: "谨以此册，留住那两年" },
    { t: "title", text: "一段不会重来的青春。\n照片都在，日子也还在。" },
    { t: "toc", note: "从初二到初三，一页一页，慢慢翻。" },
    { t: "prologue", label: "序 · 写在翻开之前",
      text: "照片是按时间排好的，记忆却不是。\n有些画面清楚得像昨天，有些只剩一点光和颜色。\n那些没对准焦的、拍歪了的、手挡住镜头的，都留着。\n当时只觉得普通，后来才知道，那就是那两年。",
      sign: "—— 整理这些照片的人" },

    /* ---------- 01 初二 · 故事的开始 ---------- */
    { t: "chapter", id: "ch1", tone: "tone-1", photo: "90bc73" },
    { t: "spread", photo: "0d42af", noteL: "刚开始", noteR: "2024 年 11 月" },
    { t: "full", photo: "6c1147", cap: "都还在。" },
    { t: "collage", title: "校运会那几天", sub: "2024.11 · 操场与看台",
      photos: [
        { id: "3fec40", cap: "两个人" }, { id: "56ae8a", cap: "合影" },
        { id: "e3f49e" }, { id: "b94071", cap: "乒乓球台" },
        { id: "21f700" }, { id: "59f420", cap: "一抬头" }
      ] },
    { t: "duo", orient: "vertical", head: "展厅里，人来人往", foot: "2024.11.08",
      photos: [{ id: "c488c7", cap: "围坐在一起" }, { id: "6d0024", cap: "展板前" }] },
    { t: "frame", photo: "df7b7b", rotate: -1.8, top: "校庆 · 舞台边",
      written: "四个人", quote: "快门按下去的时候，什么也没想。",
      meta: "2024.11.28" },
    { t: "quote", text: "有些日子，\n当时只道是寻常。", note: "初二上" },

    { t: "full", photo: "ae8969", cap: "研学那天，先拍一张。" },
    { t: "collage", title: "五月，出了一趟门", sub: "2025.05.30 · 研学",
      photos: [
        { id: "a36980", cap: "比个耶" }, { id: "e63c03", cap: "两个人" },
        { id: "5c3960" }, { id: "0d6a7d", cap: "笑一个" },
        { id: "c25a22", cap: "车上" }, { id: "47f006", cap: "午饭" }
      ] },
    { t: "duo", orient: "horizontal", head: "集合，出发，回来", foot: "",
      photos: [{ id: "e1c32f", cap: "舞台前" }, { id: "138d47", cap: "桥上" }] },
    { t: "timeline", head: "初二这一年的几个日子", sub: "日期来自照片本身",
      items: [
        { id: "3fec40", date: "auto", text: "校运会与校庆" },
        { id: "47f006", date: "auto", text: "研学路上" },
        { id: "969e0b", date: "auto", text: "游乐设施前" },
        { id: "ae6388", date: "auto", text: "学期末的教室" }
      ] },
    { t: "duo", orient: "vertical", head: "七月，学期最后几天", foot: "",
      photos: [{ id: "6b8a09", cap: "黑板前" }, { id: "d38b73", cap: "课间" }] },
    { t: "frame", photo: "841267", rotate: 1.6, top: "教室窗边",
      written: "窗外的光", quote: "一整个下午，就这样过去了。", meta: "2025.07.04" },

    /* ---------- 02 少年日常 · 镜头里的我们 ---------- */
    { t: "chapter", id: "ch2", tone: "tone-2", photo: "08ce2a" },
    { t: "collage", title: "没什么事发生的下午", sub: "镜头忽然转过来的时候",
      photos: [
        { id: "0a6e4b" }, { id: "ed0f95", cap: "课桌前" },
        { id: "7957d4", cap: "鱼眼" }, { id: "2da784", cap: "眼镜" },
        { id: "19043b" }, { id: "a32595", cap: "回头" }
      ] },
    { t: "frame", photo: "32b9fa", rotate: -2.2, top: "教室",
      written: "两个人", quote: "没有谁特意站好。", meta: "" },
    { t: "duo", orient: "horizontal", head: "看镜头", foot: "",
      photos: [{ id: "ddc4da", cap: "四个人" }, { id: "d24550", cap: "并排" }] },
    { t: "spread", photo: "a11dca", noteL: "操场从上面看", noteR: "是这样子的" },
    { t: "full", photo: "0ee37a", cap: "后来常常想起的，是这种没什么事的时候。" },
    { t: "collage", title: "课桌上的东西", sub: "笔、本子、卷子和手",
      photos: [
        { id: "6b1bb6" }, { id: "cf8d14", cap: "同桌" },
        { id: "6e666e" }, { id: "539cf3" }, { id: "cc89bc" }
      ] },
    { t: "timeline", head: "几个普通的日子", sub: "日期来自照片本身",
      items: [
        { id: "08ce2a", date: "auto", text: "课间" },
        { id: "b4b5c5", date: "auto", text: "低头看书" },
        { id: "5db746", date: "auto", text: "礼堂的红色座椅" },
        { id: "1267ad", date: "auto", text: "期末那几天" }
      ] },
    { t: "duo", orient: "vertical", head: "两个人，或者一个人", foot: "",
      photos: [{ id: "c0eadd", cap: "并肩" }, { id: "6d11dd", cap: "躺着聊天" }] },
    { t: "quote", text: "书还摊着，\n人已经走开了。", note: "日常" },
    { t: "frame", photo: "beda95", rotate: 1.2, top: "窗边",
      written: "再看一眼", quote: "时间在这里慢了一下。", meta: "2026.07.02" },
    { t: "duo", orient: "horizontal", head: "安静的时候", foot: "",
      photos: [{ id: "77ed2e", cap: "做题" }, { id: "5db746", cap: "翻书" }] },
    { t: "collage", title: "纸和笔", sub: "",
      photos: [
        { id: "8d90bd" }, { id: "5056c5" },
        { id: "06b603", cap: "手写" }, { id: "d718f3", cap: "低头" }
      ] },

    /* ---------- 03 初三 · 时间开始加速 ---------- */
    { t: "chapter", id: "ch3", tone: "tone-3", photo: "b4b5c5" },
    { t: "full", photo: "d84357", cap: "人齐的时候，总有人喊拍照。" },
    { t: "duo", orient: "vertical", head: "这一年，桌子上的东西变多了", foot: "",
      photos: [{ id: "f91de1", cap: "做题" }, { id: "7e8947", cap: "写字" }] },
    { t: "spread", photo: "d07260", noteL: "校运会", noteR: "2025 年 11 月" },
    { t: "collage", title: "彩色的烟，和跑起来的人", sub: "2025.11.13 — 11.14",
      photos: [
        { id: "9f743a" }, { id: "abc2f0" }, { id: "1a6b04", cap: "俯拍" },
        { id: "7aea60" }, { id: "3b7f96", cap: "跑道" }
      ] },
    { t: "frame", photo: "7ee2a5", rotate: -1.3, top: "三月 · 操场",
      written: "2026", quote: "数字举起来的时候，才发现这一年真的到了。", meta: "2026.03.22" },
    { t: "timeline", head: "初三的几个节点", sub: "日期来自照片本身",
      items: [
        { id: "e5da94", date: "auto", text: "教室里的屏幕" },
        { id: "d84357", date: "auto", text: "校运会合影" },
        { id: "7ee2a5", date: "auto", text: "操场上的 2026" },
        { id: "47ce49", date: "auto", text: "研学那天" }
      ] },
    { t: "duo", orient: "horizontal", head: "一月，学期末", foot: "",
      photos: [{ id: "1267ad", cap: "礼堂" }, { id: "bccf3f", cap: "教室" }] },
    { t: "quote", text: "走廊很长，\n课间很短。", note: "初三" },
    { t: "full", photo: "b9d3b2", cap: "还是爱笑。" },
    { t: "collage", title: "四月底，又出了一趟门", sub: "2026.04.29 · 研学",
      photos: [
        { id: "88bb8d", cap: "车上睡着了" }, { id: "c2e878" },
        { id: "95f350", cap: "回头" }, { id: "40cdee", cap: "围坐" },
        { id: "52e196" }
      ] },

    /* ---------- 04 那些重要的人 ---------- */
    { t: "chapter", id: "ch4", tone: "tone-4", photo: "abe9e4" },
    { t: "spread", photo: "aeefa4", noteL: "一整间教室", noteR: "都在里面" },
    { t: "full", photo: "0353e1", cap: "有些名字不用写下来。" },
    { t: "collage", title: "合影", sub: "没有按身高排，也没有数够人数",
      photos: [
        { id: "abe9e4" }, { id: "3f7e3c", cap: "窗边" },
        { id: "209d0d" }, { id: "6c1599" },
        { id: "10ffc2", cap: "举杯" }, { id: "7f1c66" }
      ] },
    { t: "frame", photo: "8d5116", rotate: 2.1, top: "教室门口",
      written: "三个人", quote: "后来各自走出了校门，照片还留在同一页。", meta: "2025.07.04" },
    { t: "quote", text: "镜头里的位置，\n总是刚好。", note: "给照片里的人" },

    /* ---------- 05 青春散场 · 毕业与告别 ---------- */
    { t: "chapter", id: "ch5", tone: "tone-5", photo: "01f992" },
    { t: "spread", photo: "77acfc", noteL: "七月二日", noteR: "礼堂" },
    { t: "full", photo: "e8958b", cap: "花抱在手里，照片拍完了。" },
    { t: "collage", title: "最后一天", sub: "2026.07.02",
      photos: [
        { id: "e05676", cap: "证书" }, { id: "93551f" },
        { id: "498f85", cap: "黑板" }, { id: "5ea99c", cap: "桌上的花" },
        { id: "c8a99f", cap: "横幅" }
      ] },
    { t: "duo", orient: "vertical", head: "又回头拍了这些", foot: "没有人的照片",
      photos: [{ id: "b8d454", cap: "教学楼" }, { id: "ac5871", cap: "楼之间" }] },
    { t: "quote", text: "风从走廊那头过来，\n和两年前一样。", note: "散场" },
    { t: "full", photo: "d569ac", cap: "照片摊在桌上，还没收起来。" },
    { t: "collage", title: "操场上", sub: "",
      photos: [
        { id: "229dad" }, { id: "befebd", cap: "跑起来" },
        { id: "714e23", cap: "红旗" }, { id: "bd0e06" }
      ] },
    { t: "duo", orient: "horizontal", head: "抬头看天", foot: "",
      photos: [{ id: "ebeb70", cap: "林荫" }, { id: "22d1c6", cap: "云" }] },

    /* ---------- 06 尾声 ---------- */
    { t: "chapter", id: "ch6", tone: "tone-1", photo: "91793f" },
    { t: "quote", text: "原来那些平凡的日子，\n后来都成了最想念的日子。" },
    { t: "letter", head: "写给那时候的自己：",
      paras: [
        "你现在大概还觉得，这两年长得望不到头。",
        "课间的十分钟，走廊尽头的光，放学时总也走不完的那段路，\n都平常得很。",
        "后来它们被收进一个文件夹里，偶尔点开，\n才发现每一张都舍不得删。",
        "不用急着长大，也不用特意记住什么。\n该留下的，自己会留下。"
      ],
      sign: "—— 翻完这本册子的我" },
    { t: "endpaperBack", text: "故事没有结束" },
    { t: "backcover", text: "故事没有结束" }
  ]
};
