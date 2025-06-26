import os
from projekt.backend.utils.pdf_utils import (merge_pdfs_by_rating, markdown_to_pdf)
from projekt.backend.utils.html_parser import (extract_text_from_selector,extract_attribute_from_selector)


COVERLETTERS = {
    "Alice": (
        """
**Alice Mustermann**
Musterstraße 12  
80331 München  
alice.mustermann@email.de  
0170 1234567

**Hochschule München**  
Personalabteilung  
Herrn/Frau [Name des Ansprechpartners]  
Lothstraße 13c  
80335 München

München, 26. Juni 2025

**Bewerbung als Werkstudentin im Bereich Informationstechnologie**

Sehr geehrte Damen und Herren,

mit großem Interesse habe ich Ihre Stellenausschreibung auf der Karriereseite der
Hochschule München gelesen. Als Studentin der Wirtschaftsinformatik – Informationstechnologie
bringe ich:

- Fundierte Kenntnisse in Softwareentwicklung, Datenbankmanagement und Netzwerkinfrastruktur  
- Praktische Erfahrung in agiler Webentwicklung  
- Analytische Denkweise, schnelle Auffassungsgabe und Teamfähigkeit  

Ich freue mich darauf, mein Engagement in Ihr IT-Team einzubringen und aktiv an Ihren
Projekten mitzuwirken.

Über eine Einladung zum persönlichen Gespräch freue ich mich sehr.

Mit freundlichen Grüßen

**Alice Mustermann**
        """,
        6
    ),

    "Bob": (
        """
**Bob Beispielmann**  
Beispielweg 5  
81675 München  
bob.beispielmann@email.de  
0171 7654321

**Hochschule München**  
Personalabteilung  
Herrn/Frau [Name des Ansprechpartners]  
Blumenstraße 7  
80331 München

München, 26. Juni 2025

**Bewerbung als Werkstudent im Bereich IT-Support und Systemadministration**

Sehr geehrte Damen und Herren,

als engagierter Student der Wirtschaftsinformatik – Informationstechnologie bringe ich:

- Fundierte Kenntnisse in Betriebssystemen und Netzwerksicherheit  
- Erfahrung in Systemkonfiguration, Support und Fehlerbehebung  
- Strukturierte Arbeitsweise und ausgeprägte Serviceorientierung  

Gerne unterstütze ich Ihre IT-Abteilung als Werkstudent und vertiefe dabei meine praktischen Fähigkeiten.

Ich freue mich auf Ihre Rückmeldung und ein persönliches Gespräch.

Mit freundlichen Grüßen

**Bob Beispielmann**
        """,
        9
    )
}

SAMPLE_HTML = """
<div id="content">
Dies ist der   Haupttext.
Er hat mehrere     Leerzeichen.
</div>
<ul class="nav-links">
<li><a href="/home">Home</a></li>
<li><a href="/about">Über uns</a></li>
<li><a href="/contact">Kontakt</a></li>
</ul>
  """

def main():
    sample_html = """
    <div id="content">
      Dies ist der   Haupttext.
      Er hat mehrere     Leerzeichen.
    </div>
    <ul class="nav-links">
      <li><a href="/home">Home</a></li>
      <li><a href="/about">Über uns</a></li>
      <li><a href="/contact">Kontakt</a></li>
    </ul>
    """

    text = extract_text_from_selector(sample_html, "#content")
    print("=== Extrahierter Text ===")
    if text:
        print(text)
    else:
        print("<kein Text gefunden>")

    print()

    links = extract_attribute_from_selector(sample_html,".nav-links a","href")
    print("=== Extrahierte Links ===")
    if links:
        for url in links:
            print("-", url)
    else:
        print("<keine Links gefunden>")


    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(base_dir, "pdf_output")

    os.makedirs(out_dir, exist_ok=True)

    for name, (text, rating) in COVERLETTERS.items():
        filename = f"{rating}_{name}.pdf"
        dest = os.path.join(out_dir, filename)
        markdown_to_pdf(cover_letter=text, dest=dest, title=name, link="https://hm.edu/index.de.html",rating=rating)



if __name__ == "__main__":
    main()

