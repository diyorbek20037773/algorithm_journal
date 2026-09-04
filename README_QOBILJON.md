# Qobiljon uchun yo'riqnoma — Claude Code ga topshiriqni qanday berish

## Papkadagi fayllar

| Fayl | Kim uchun | Nima |
|---|---|---|
| `CLAUDE.md` | Claude Code | Ish qoidalari: savol bermaslik, qarorlar, git/push, fazalar, "done" mezonlari, HANDOFF |
| `SPEC.md` | Claude Code | To'liq texnik spetsifikatsiya (ma'lumotlar modeli, URL lar, workflow, integratsiyalar, seed, 8 faza, 18 qabul testi) |
| `DESIGN_BRIEF.md` | Claude Design **va** Claude Code | Dizayn tizimi (ranglar, shriftlar, komponentlar), 18 ta sahifa ro'yxati, logo variantlari. `design/` papka bo'lmasa ham Claude Code shu hujjat bo'yicha dizaynni o'zi qiladi |
| `TEXNIK_TOPSHIRIQ.md` | Sen / muassis / shartnoma | Rasmiy TZ (kirill), Django uchun qayta ishlangan. Word ga o'tkazib imzolatsa bo'ladi |
| `PROMPT.txt` | Sen | Claude Code ga birinchi xabar sifatida ko'chirib tashlaydigan matn |

## Qadamlar

1. Kompyuterda bo'sh papka och: `algorithm_journal`.
2. Shu 5 ta faylni o'sha papkaga ko'chir (README_QOBILJON.md ni ko'chirmasa ham bo'ladi).
3. **Ixtiyoriy, lekin tavsiya:** avval Claude Design ga `DESIGN_BRIEF.md` ni berib, natijani `algorithm_journal/design/` papkasiga saqla. Claude Design ga prompt:
   > "Read DESIGN_BRIEF.md and produce every artboard listed in §5 (desktop 1440 + mobile 390), the 3 logo variants in §3, and tokens.css, exactly in the deliverable format of §7. Output into a folder named design/."
   Vaqt bo'lmasa — o'tkazib yubor, Claude Code brief bo'yicha o'zi qiladi.
4. Terminalda papkaga kir va Claude Code ni ishga tushir:
   ```
   cd algorithm_journal
   claude
   ```
   Uzoq avtonom ish uchun ruxsat so'rashlarini kamaytirish: `claude --permission-mode acceptEdits` (yoki sessiya ichida `/permissions` orqali Bash, Edit, Write ga "always allow"). Agar to'liq nazoratsiz ishlashi kerak bo'lsa: `claude --dangerously-skip-permissions` (faqat shu papkada, muhim fayllar yo'q bo'lgan kompyuterda).
5. GitHub push ishlashi uchun oldindan bir marta: `gh auth login` (yoki git credential sozlangan bo'lsin). Bo'lmasa Claude Code lokal commit qiladi, HANDOFF.md da push buyrug'ini yozib qoldiradi.
6. `PROMPT.txt` ichidagi matnni to'liq ko'chirib, Claude Code ga yubor. Ketdi.
7. Qaytib kelganda birinchi `PROGRESS.md`, keyin `HANDOFF.md`, keyin `docs/screenshots/` ni ko'r.

## Sen keyin to'ldirishing kerak bo'lgan narsalar (tizim ular yo'q bo'lsa ham ishlaydi)

- Tahrir hay'ati ro'yxati (admin panel orqali, DEMO yozuvlar o'rniga).
- e-ISSN, OAV guvohnomasi raqami/sanasi, muassis nomi va manzili (admin → Site settings).
- Crossref a'zoligi ($275/yil) → DOI prefiks → `.env` ga `DOI_PREFIX`, `CROSSREF_USER/PASSWORD`, `CROSSREF_TEST=false`.
- ORCID Public API kalitlari (bepul) → `.env`.
- Resend (yoki boshqa SMTP) → `.env`; domenga SPF/DKIM.
- Domen (`algorithm-journal.uz` tavsiya) va O'zbekistondagi VPS (4 vCPU / 8 GB / 100 GB).
- Logo: Claude Design variantlaridan birini tanlab `static/img/logo/` ga qo'yish (yoki admin orqali yuklash).

## Byudjet (yillik, taxminan)

Crossref $275 + DOI $1/maqola · Similarity Check ~$50 (ixtiyoriy) · CLOCKSS yoki Portico ~$275 · domen ~$20 · VPS ~$30–60/oy · Resend bepul tarif yetadi.
