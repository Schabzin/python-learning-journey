isbn_cell = ws[f"A{r}"]
isbn_cell.fill = fill(LORANGE)
isbn_cell.font = font(size=9, color=BLACK)
isbn_cell.border = border()
isbn_cell.alignment = align("center")
isbn_cell.number_format = "@"