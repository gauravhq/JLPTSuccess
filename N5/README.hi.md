# JLPT N5 ट्यूटर

> **NOTICE (Phase 1 launch, 2026-05-24):** The Hindi UI is **temporarily disabled** in the live app while the English-medium launch ships. All Hindi content (`locales/hi.json`, `meaning_hi`, `explanation_hi` across the corpus) is **retained intact** in the build: no data has been removed. The Hindi locale toggle and Hindi option in Settings will return in **Phase 2** by widening `ENABLED_LOCALES` in [`js/i18n.js`](js/i18n.js). This Hindi README will continue to be maintained.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](../LICENSE)
[![Content: CC BY-SA 4.0](https://img.shields.io/badge/Content-CC%20BY--SA%204.0-lightgrey.svg)](CONTENT-LICENSE.md)
[![JLPT Level: N5](https://img.shields.io/badge/JLPT-N5-14452a.svg)](https://gauravaccentureproducts.github.io/JLPTSuccess/N5/)
[![PWA](https://img.shields.io/badge/PWA-installable-brightgreen.svg)](https://gauravaccentureproducts.github.io/JLPTSuccess/N5/)
[![Locales: EN · HI](https://img.shields.io/badge/locales-EN%20%C2%B7%20HI-blueviolet.svg)](docs/TRANSLATING.md)
[![Privacy: no telemetry](https://img.shields.io/badge/privacy-no%20telemetry-success.svg)](PRIVACY.md)

> **कोई लॉगिन नहीं · कोई ट्रैकिंग नहीं · ऑफ़लाइन काम करता है · ओपन सोर्स · 100% डिवाइस पर · मुफ़्त, विज्ञापन नहीं, पेवॉल नहीं।**

JLPT N5 की तैयारी के लिए ब्राउज़र-आधारित स्थैतिक वेब ऐप: व्याकरण, शब्दावली, कान्जी, पठन और श्रवण। **कोई सर्वर नहीं। कोई खाता नहीं। कोई तृतीय-पक्ष स्क्रिप्ट नहीं।** बिल्ड टूल (Python) `/tools/` में रहते हैं; सीखने वाला केवल ब्राउज़र चलाता है।

> **रणनीतिक ध्यान-केंद्रित: हिंदी (निच-N1)।** ऐप पहले 5 भाषाएँ (en/vi/id/ne/zh) समर्थन करता था। बाज़ार अनुसंधान में पाया गया कि **हिंदी एक अनोखा "उच्च माँग, कम प्रतिस्पर्धा" अंतराल है**: भारत JLPT में 5वाँ सबसे बड़ा देश है (~50,000 आवेदक/वर्ष; 73% N5 या N4 स्तर पर); पर समर्पित हिंदी-माध्यम तैयारी ऐप मौजूद नहीं है। 2026-05-06 को ऐप ने en + hi पर ध्यान-केंद्रित किया, और राउंड-9 (2026-05-07, **v1.12.50**) तक **पूरी सामग्री पर हिंदी समीक्षा शत-प्रतिशत** हो चुकी है: LLM-व्यक्तित्व-Q33 गुणवत्ता-स्तर पर।

## विशेषताएँ (v1.12.50: राउंड-9 समापन)

- **178 N5 व्याकरण पैटर्न**: सब पर ≥4 उदाहरण, सब पर सामान्य-गलती, **सब 178 पर हिंदी-L1 नोट्स (`l1_notes.hi`)**।
- **1,041 N5 शब्दावली प्रविष्टियाँ**: सब पर हिंदी अनुवाद (`gloss_hi`), 134 क्रियाओं पर `verb_class` (godan / ichidan / irregular) + 6 X-6.6 अपवाद-क्रियाओं पर `group1_exception` ध्वज, 87 संज्ञाओं पर counter, उच्च-आवृत्ति प्रविष्टियों पर पिच-स्वर + सहयोगी-शब्द।
- **106 N5 कान्जी**: सब पर हिंदी अर्थ (`meanings_hi`), मूलाधार विघटन, स्मृति-संकेत, समान-दिखने वाले समूह, ≥3 उदाहरण।
- **45 पठन अनुच्छेद**: सब पर हिंदी सारांश (`summary_hi`), सांस्कृतिक संदर्भ (`cultural_context`) जहाँ Japan-विशिष्ट हो।
- **47 श्रवण अभ्यास**: **VOICEVOX बहु-स्वर ऑडियो** (4 अलग वक्ता: Shikoku Metan / Shirakami Kotaro / Hau Tsumugi / Aoyama Ryusei), JLPT-N5 गति-लक्ष्य 180-240 morae/min, सब पर हिंदी व्याख्या (`explanation_hi`)।
- **426 मॉक-परीक्षा प्रश्न (29 पेपर)**: मोजी / गोई / बुनपोऊ / दोक्काइ + chokai virtual paper; **पूर्ण-मॉक पेपर (85 प्रश्न × 105 मिनट)** असली JLPT N5 आकार से मेल खाते हैं।
- **एकीकृत दैनिक समीक्षा कतार (FSRS-4.5)**: व्याकरण + शब्दावली + कान्जी एक ही समीक्षा सूची में।
- **प्रथम-बार उपयोगकर्ता के लिए शुरुआती-पैक**: होम पर 5 मूलभूत पैटर्न (です／〜ます, は, Verb-ます, い-Adjectives, か) का क्यूरेटेड पथ।
- **पूरी तरह से ऑफ़लाइन काम करता है**: सेवा कर्मचारी (service worker) पूरा शेल कैश करता है। पहली ऑनलाइन यात्रा के बाद बिना नेटवर्क काम करता है।

## स्थानीय रूप से चलाएँ

```bash
git clone https://github.com/gauravaccentureproducts/JLPTSuccess.git
cd JLPTSuccess
python -m http.server 8000
# ब्राउज़र में: http://localhost:8000/N5/
```

## हिंदी अनुवाद में योगदान

देखें [`docs/TRANSLATING.md`](docs/TRANSLATING.md): हिंदी UI / सामग्री समीक्षा कार्यप्रवाह।

## निजता (Privacy)

- कोई लॉगिन नहीं • कोई ट्रैकिंग नहीं • कोई विज्ञापन नहीं • कोई पेवॉल नहीं
- सारी प्रगति आपके ब्राउज़र के localStorage में रहती है (नामस्थान `jlpt-n5-tutor:*`)
- कोई दूरस्थ API कॉल सामान्य उपयोग में नहीं

देखें [`PRIVACY.md`](PRIVACY.md) (अंग्रेज़ी)।

## लाइसेंस

- **कोड**: MIT, देखें `../LICENSE`।
- **शैक्षिक सामग्री**: CC BY-SA 4.0, देखें `CONTENT-LICENSE.md`।
- **तृतीय-पक्ष**: KanjiVG (CC BY-SA 3.0), Inter, Noto Sans JP, देखें `NOTICES.md`।

## निर्माता-नोट

यह दस्तावेज़ अंग्रेज़ी [`README.md`](README.md) का हिंदी संस्करण है: संक्षिप्त रूप में। पूरी विकास / स्व-होस्टिंग गाइड के लिए मूल README देखें।

---

*अनुप्रयोग 2026-05-06 (v1.12.40+) से EN + HI दो भाषाएँ समर्थन करता है। पुरानी 5-भाषा शाखा (en/vi/id/ne/zh) कमिट इतिहास में `pre-locale-transition` टैग पर सुरक्षित है।*
