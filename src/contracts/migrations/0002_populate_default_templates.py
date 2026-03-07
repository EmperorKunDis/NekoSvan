"""Populate default contract and email templates."""

from django.db import migrations


def create_templates(apps, schema_editor):
    ContractTemplate = apps.get_model("contracts", "ContractTemplate")

    templates = [
        {
            "name": "Smlouva o dilo",
            "is_active": True,
            "body_template": """<h1>SMLOUVA O DÍLO</h1>
<p>uzavřená dle § 2586 a násl. zákona č. 89/2012 Sb., občanský zákoník</p>
<hr>

<h2>Smluvní strany</h2>
<p><strong>Objednatel:</strong><br>
{{client_name}}<br>
{{client_company}}<br>
IČO: {{client_ico}}</p>

<p><strong>Zhotovitel:</strong><br>
ADNP s.r.o.<br>
ve spolupráci s NekoSvan s.r.o. a Praut s.r.o.</p>

<h2>Předmět smlouvy</h2>
<p>Zhotovitel se zavazuje provést pro objednatele dílo dle specifikace v příloze č. 1 (technická specifikace).</p>

<h2>Cena díla</h2>
<p>Celková cena: <strong>{{total_price}} Kč</strong> bez DPH</p>
<p>Záloha: <strong>{{deposit_amount}} Kč</strong> (splatná do 7 dnů od podpisu)</p>

<h2>Termín plnění</h2>
<p>Zahájení prací: do 5 pracovních dnů od připsání zálohy.</p>

<h2>Podmínky</h2>
<p>Dílo bude předáváno po milnících. Každý milník podléhá schválení objednatelem.</p>

<p>V {{date}}</p>
<br><br>
<p>_________________________&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_________________________</p>
<p>Objednatel&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Zhotovitel</p>""",
        },
        {
            "name": "Email: Nabidka klientovi",
            "is_active": True,
            "body_template": """<p>Dobrý den, {{client_name}},</p>

<p>děkujeme za Váš zájem o naše služby. Na základě naší analýzy Vašich požadavků
jsme pro Vás připravili cenovou nabídku.</p>

<h3>Shrnutí nabídky</h3>
<p><strong>Celková cena:</strong> {{total_price}} Kč bez DPH<br>
<strong>Záloha:</strong> {{deposit_amount}} Kč</p>

<p>Součástí nabídky je demo ukázka, kterou si můžete prohlédnout na přiloženém odkazu.</p>

<p>V případě zájmu nebo dotazů nás neváhejte kontaktovat.</p>

<p>S pozdravem,<br>
Tým ADNP × NekoSvan × Praut</p>""",
        },
        {
            "name": "Email: Potvrzeni zalohy",
            "is_active": True,
            "body_template": """<p>Dobrý den, {{client_name}},</p>

<p>potvrzujeme přijetí zálohy ve výši <strong>{{deposit_amount}} Kč</strong>
pro projekt společnosti {{client_company}}.</p>

<p>Práce na projektu budou zahájeny do 5 pracovních dnů. O průběhu Vás budeme
pravidelně informovat prostřednictvím klientského portálu.</p>

<p>S pozdravem,<br>
Adam — ADNP s.r.o.</p>""",
        },
        {
            "name": "Email: Predani milniku",
            "is_active": True,
            "body_template": """<p>Dobrý den, {{client_name}},</p>

<p>rádi bychom Vás informovali, že milník Vašeho projektu je připraven ke kontrole.</p>

<p>Prosíme o jeho schválení nebo zaslání připomínek prostřednictvím klientského portálu.</p>

<p>Odkaz na portál: <em>(bude doplněn automaticky)</em></p>

<p>S pozdravem,<br>
Vadim — obchodní zástupce</p>""",
        },
        {
            "name": "Email: Dokonceni projektu",
            "is_active": True,
            "body_template": """<p>Dobrý den, {{client_name}},</p>

<p>s radostí Vám oznamujeme, že projekt pro {{client_company}} byl úspěšně dokončen
a prošel finální kontrolou kvality.</p>

<p><strong>Celková cena:</strong> {{total_price}} Kč<br>
<strong>Zbývá uhradit:</strong> doplatek dle smlouvy</p>

<p>Veškeré podklady a přístupy Vám budou předány po připsání doplatku.</p>

<p>Děkujeme za spolupráci a těšíme se na případné další projekty.</p>

<p>S pozdravem,<br>
Tým ADNP × NekoSvan × Praut</p>""",
        },
    ]

    for tmpl_data in templates:
        ContractTemplate.objects.get_or_create(
            name=tmpl_data["name"],
            defaults=tmpl_data,
        )


def remove_templates(apps, schema_editor):
    ContractTemplate = apps.get_model("contracts", "ContractTemplate")
    ContractTemplate.objects.filter(
        name__in=[
            "Smlouva o dilo",
            "Email: Nabidka klientovi",
            "Email: Potvrzeni zalohy",
            "Email: Predani milniku",
            "Email: Dokonceni projektu",
        ]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("contracts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_templates, remove_templates),
    ]
