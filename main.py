from deep_translator import GoogleTranslator
import fitz
import time

translator = GoogleTranslator(source='auto', target='en')

doc = fitz.open('pdf.pdf')

new_pdf = fitz.open()

for page_number in range(doc.page_count):
    print(f"Traduzindo página {page_number + 1}/{doc.page_count}...")
    start_time = time.time()

    page = doc.load_page(page_number)
    text_block = page.get_text("dict")["blocks"]
    img_list = page.get_images(full=True)

    new_page = new_pdf.new_page(width=page.rect.width, height=page.rect.height)

    for img in img_list:
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        
        if len(img) > 2 and isinstance(img[2], tuple) and len(img[2]) == 4:
            img_rect = fitz.Rect(*img[2])
        else:
            continue
        
        new_page.insert_image(img_rect, stream=image_bytes)

    for block in text_block:
        if 'lines' in block:
            block_text = ''
            for line in block['lines']:
                for span in line['spans']:
                    block_text += span['text'] + ' '

            try:
                translation = translator.translate(block_text)
            except Exception as e:
                print(f"Erro ao traduzir o texto na página {page_number + 1}: {e}")
                translation = block_text  

            new_page.insert_text((block['bbox'][0], block['bbox'][1]), translation, fontsize=13)

    end_time = time.time()
    print(f"Página {page_number + 1} traduzida em {end_time - start_time:.2f} segundos.")

new_pdf.save('pdftraduzido.pdf')
new_pdf.close()
doc.close()

print('Tradução concluída e PDF salvo com sucesso!')
