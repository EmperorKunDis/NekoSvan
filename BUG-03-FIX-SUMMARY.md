# BUG-03: Document Upload Fix

**Datum:** 2026-03-10  
**Status:** ✅ Opraveno

## Problém
`POST /api/v1/pipeline/lead-from-document/` vracel 400 Bad Request bez detailních chybových zpráv.

## Příčiny
1. **Backend view** přímo přistupovala k `request.FILES.get("file")` místo použití `serializer.validated_data`
2. **Serializer** měl základní validaci, ale bez detailních error messages
3. **Frontend** neukazoval konkrétní validační chyby z DRF

## Provedené opravy

### 1. Backend View (`src/pipeline/views.py`)
**Změna:** View nyní používá `serializer.validated_data.get("file")` místo `request.FILES.get("file")`

```python
# PŘED:
document = LeadDocument.objects.create(
    file=request.FILES.get("file"),  # ❌ přímý přístup k request.FILES
    ...
)

# PO:
document = LeadDocument.objects.create(
    file=serializer.validated_data.get("file"),  # ✅ použití validated_data
    ...
)
```

**Důvod:** Zajišťuje že soubor prošel validací serializeru. Pokud serializer odmítne file (špatný formát, chybějící pole), view to správně zachytí.

### 2. Serializer (`src/pipeline/serializers.py`)
**Přidáno:**
- Detailní `error_messages` pro každé pole
- Validace formátu souboru (`.txt`, `.pdf`, `.doc`, `.docx`, `.eml`)
- Strukturované chybové zprávy s field-specific detaily

```python
file = serializers.FileField(
    required=False,
    allow_null=True,
    help_text="Soubor (TXT, PDF, DOC, DOCX, EML)",
    error_messages={
        "invalid": "Nahraný soubor je neplatný. Podporované formáty: ...",
        "empty": "Nahraný soubor je prázdný.",
    },
)

def validate(self, attrs):
    # Kontrola že alespoň jedno pole je vyplněno
    if not file and not raw_text:
        raise serializers.ValidationError({
            "file": "Musíte nahrát soubor nebo vložit text.",
            "raw_text": "Musíte nahrát soubor nebo vložit text.",
        })
    
    # Validace formátu souboru
    if file:
        allowed_extensions = [".txt", ".pdf", ".doc", ".docx", ".eml"]
        if not any(file.name.lower().endswith(ext) for ext in allowed_extensions):
            raise serializers.ValidationError({
                "file": f"Nepodporovaný formát souboru. Povolené: {', '.join(allowed_extensions)}"
            })
    
    return attrs
```

### 3. Frontend (`frontend/src/app/features/deals/deal-from-document.component.ts`)
**Přidáno:**
- Úvodní `/` v URL: `/api/v1/pipeline/lead-from-document/` (best practice)
- Lepší zpracování DRF validation errors (field-specific messages)
- Parsování strukturovaných chyb z backendu

```typescript
// Zpracování detailních validačních chyb z DRF
if (err.status === 400 && err.error) {
  if (typeof err.error === 'object') {
    const errors: string[] = [];
    
    // Field-specific errors
    for (const [field, messages] of Object.entries(err.error)) {
      if (Array.isArray(messages)) {
        errors.push(...messages);
      } else if (typeof messages === 'string') {
        errors.push(messages);
      }
    }
    
    if (errors.length > 0) {
      errorMsg = errors.join(' ');
    }
  }
}
```

### 4. Testy (`src/pipeline/tests/test_lead_from_document.py`)
**Vytvořeno:** Nový test suite s testy pro:
- ✅ Vytvoření leadu z textu
- ✅ Vytvoření leadu ze souboru
- ✅ Validace chybějících dat (400)
- ✅ Validace neplatného formátu souboru (400)
- ✅ Autentizace (401)

## Výsledek
- ✅ Backend validuje file field správně přes serializer
- ✅ 400 chyby nyní obsahují konkrétní detail co chybí/je špatně
- ✅ Frontend zobrazuje uživatelsky přívětivé chybové zprávy
- ✅ Přidána validace formátu souboru
- ✅ Code má jednotkové testy

## Testování
```bash
# Spustit testy
pytest src/pipeline/tests/test_lead_from_document.py -v

# Nebo celý pipeline app
pytest src/pipeline/tests/ -v
```

## Typické chybové zprávy (nyní):
- `"Musíte nahrát soubor nebo vložit text."` - chybí file i raw_text
- `"Nepodporovaný formát souboru. Povolené: .txt, .pdf, .doc, .docx, .eml"` - neplatný formát
- `"Nahraný soubor je prázdný."` - prázdný soubor
- Backend errors z `document_service` (extrakce textu, AI parsing, atd.)

## Soubory změněny
1. `src/pipeline/views.py` - oprava použití validated_data
2. `src/pipeline/serializers.py` - detailní validace a error messages
3. `frontend/src/app/features/deals/deal-from-document.component.ts` - lepší error handling
4. `src/pipeline/tests/test_lead_from_document.py` - nový test suite
