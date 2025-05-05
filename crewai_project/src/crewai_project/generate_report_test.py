from jinja2 import Environment, FileSystemLoader
import pdfkit

def generate_report(data):
    template_dir = 'D:/Stage_PFE/CrewAI/crewai_project/src/crewai_project/'
    template_file = 'pentest_report_template.html'

    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)

    html_out = template.render(data)

    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    options = {
        'enable-local-file-access': None
    }

    pdfkit.from_string(html_out, 'pentest_report.pdf', configuration=config, options=options)

# Exemple de données
data = {
    "client_name": "ACME Corp",
    "report_date": "2025-04-28",
    "executive_summary": "Résumé rapide...",
    "nmap_results": "Ports ouverts : 22, 80, 443",
    "zap_results": "Détection d'injections XSS.",
    "sqlmap_results": "Aucune vulnérabilité SQL détectée.",
    "conclusion": "Actions recommandées : patcher serveur web."
}

generate_report(data)

