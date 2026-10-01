<div dir="rtl" lang="he">

> **הערה:** זהו פרויקט ב׳ הישן (Document Intelligence Service), שהועבר לכאן כפי שהוא. הוא אינו מחובר ל-`/learn project`, והוא אינו מסלול ב׳ החדש (PRD D5).

## פרויקט ב: Document Intelligence Service

**מודולים נדרשים:** 1 (Claude Code) + 2 (Webhooks, Structured Output, Python)
**זמן מוערך:** 12 שעות
**רמת קושי:** בינונית-גבוהה

### מה בונים

שירות ווב שמקבל מסמכים (PDF, CSV, URL לאתר) ומחזיר נתונים מובנים — עם Gemini Structured Output + Pydantic schema מוגדר מראש. יש Dashboard לניהול וצפייה בתוצאות, ו-REST API לשאר המערכות. נבנה לגמרי עם Claude Code.

**הדגמה שמרשימה:** מעלים חוזה PDF → תוך 10 שניות מקבלים JSON עם: שמות הצדדים, תאריכי תוקף, סכום, וסעיפי ביטול. כולם בפורמט שאפשר לשלוח ישירות ל-CRM.

### בחירת Domain — בחרו אחד

**אפשרות 1: חוזים ומסמכים משפטיים**
Schema: `{parties, start_date, end_date, value_ils, payment_terms, termination_clauses, governing_law}`

**אפשרות 2: חשבוניות וקבלות**
Schema: `{vendor, date, items: [{description, qty, unit_price}], subtotal, vat, total, currency}`

**אפשרות 3: קורות חיים (HR)**
Schema: `{name, email, years_experience, skills, last_role, education, languages, red_flags}`

**אפשרות 4: דפי מוצר / Landing Pages**
Schema: `{product_name, pricing_tiers, key_features, target_audience, cta_text, competitors_mentioned}`

### דרישות טכניות

| רכיב | פרטים |
|-------|--------|
| **בנייה** | Claude Code |
| **Frontend** | Next.js + Tailwind — Dashboard + Upload UI |
| **API** | Next.js API Routes — upload endpoint + query endpoint |
| **Storage** | Cloudflare R2 (קבצים) + Supabase (תוצאות JSON) |
| **AI** | Gemini API — Structured Output עם Pydantic schema |
| **Deploy** | Cloudflare Pages (Next.js) |
| **Auth** | API Key פשוט בהדר לגישת ה-REST API |

### שלבי הפרויקט

**שלב 1 — Spec ו-CLAUDE.md (1 שעה)**

הגדירו את ה-Pydantic Schema המדויק שאתם מחלצים. זה ה-לב של הפרויקט:

```python
from pydantic import BaseModel, Field
from datetime import date

class ContractExtraction(BaseModel):
    parties: list[str] = Field(description="Names of all signing parties")
    start_date: date | None = Field(description="Contract start date, null if not found")
    end_date: date | None = Field(description="Contract end date or expiry")
    value_ils: float | None = Field(description="Total contract value in ILS, null if not monetary")
    payment_terms: str = Field(description="Payment schedule description")
    termination_clauses: list[str] = Field(description="Conditions under which contract can be terminated")
    confidence: float = Field(description="0-1 confidence score for the extraction")
```

כתבו `CLAUDE.md` ובקשו מ-Claude Code להקים Next.js + Supabase + Cloudflare R2.

**שלב 2 — Upload Endpoint + Gemini (4 שעות)**

בנו עם Claude Code את ה-Upload flow:
1. `POST /api/upload` — מקבל קובץ, שומר ב-R2, מחזיר `document_id`
2. עיבוד אסינכרוני: שולף קובץ מ-R2, שולח ל-Gemini עם Schema, שומר JSON ב-Supabase

```python
import os
import json
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def extract_document(file_bytes: bytes, mime_type: str, schema: type) -> dict:
    prompt = f"""Extract the following information from this document.
    Return a JSON object that strictly follows this schema:
    {schema.model_json_schema()}

    If a field cannot be found, use null. Include a confidence score (0-1).
    Return ONLY valid JSON, no explanation."""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=[
            types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
            prompt,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )

    result = json.loads(response.text)
    return schema(**result).model_dump()  # Pydantic validation
```

> **טיפ:** ה-SDK יודע לקבל את ה-Pydantic class ישירות ב-`response_schema=schema` במקום להדביק את ה-JSON Schema לתוך ה-prompt. נסו את שתי הדרכים והשוו — איזו מחזירה פחות שגיאות validation?

**שלב 3 — Dashboard (3 שעות)**

בקשו מ-Claude Code לבנות Dashboard:
- טבלת מסמכים עם סטטוס (processing / done / failed)
- לחיצה על שורה → פנל עם ה-JSON המחולץ בצורה קריאה
- כפתור Upload חדש
- סינון לפי תאריך / confidence score

**שלב 4 — REST API + Deploy (2 שעות)**

הוסיפו `GET /api/documents` ו-`GET /api/documents/{id}` עם API Key authentication בהדר.
בדקו עם curl שהחיצוני יכול לשלוף את הנתונים.

Deploy ל-Cloudflare Pages: `wrangler pages deploy`.

**שלב 5 — בדיקה End-to-End + הדגמה (2 שעות)**

העלו 5 מסמכים אמיתיים (אפשר דוגמאות). בדקו:
- accuracy: כמה שדות חולצו נכון?
- confidence score: האם מתאים?
- edge cases: מסמך סרוק גרוע, שפה אחרת, שדה חסר

חשבו עלות ל-100 מסמכים/יום — גם ב-Free Tier (האם 100 בקשות נכנסות במגבלה היומית של המודל שבחרתם?) וגם בתשלום.

### Checklist

- [ ] Pydantic Schema מוגדר עם לפחות 6 שדות + `confidence`
- [ ] Upload endpoint + עיבוד Gemini
- [ ] תוצאות JSON שמורות ב-Supabase
- [ ] Dashboard: רשימה + פנל + Upload UI
- [ ] REST API עם API Key Auth
- [ ] Deploy על Cloudflare Pages
- [ ] נבדק על 5 מסמכים אמיתיים — accuracy documented
- [ ] חישוב עלות ל-100 מסמכים/יום
- [ ] הדגמה: upload PDF בפני הכיתה ← JSON מוצג תוך 15 שניות

### עלויות משוערות

| שירות | עלות |
|--------|------|
| Gemini API — Free Tier | חינם (בכפוף למגבלת בקשות יומית — בדקו ב-AI Studio) |
| Gemini API — אם עוברים ל-Paid (100 docs/יום × ~2K tokens) | ~$2-4/חודש |
| Cloudflare Pages + R2 (10GB) | חינם / ~$1.5/חודש |
| Supabase Free | חינם |
| **סה"כ** | **חינם ב-Free Tier (עד ~$1.5 אם R2 עובר 10GB)** |

</div>
