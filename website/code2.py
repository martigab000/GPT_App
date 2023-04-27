import tabula

#pdf_path = input("url to pdf here")
#pdf_path = "context_data\payer_list\experian health claims-and-remits-payer-list.pdf"
pdf_path = "https://www.availity.com/documents/availity_edi_clearinghouse_health_plans_list.pdf"

dfs = tabula.read_pdf(pdf_path, pages='all')

for i in range(len(dfs)):
    dfs[i].to_csv(f"all_pages_table.csv")