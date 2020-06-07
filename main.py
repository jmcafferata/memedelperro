import telegram
from PIL import Image, ImageDraw, ImageFont
import os
from io import BytesIO
import requests
import re
import textwrap
import sys


def webhook(request):

    bot = telegram.Bot(token=os.environ["TELEGRAM_TOKEN"])

    if request.method == "POST":

        update = telegram.Update.de_json(request.get_json(force=True), bot)

        if update.message:

            # Chequeamos qué nos dice el usuario
            if update.message.text:

                print(update)

                chat_id = update.message.chat.id

                # Si nos dice "nuevo", arrancan las instrucciones
                if update.message.text == 'nuevo' or update.message.text == 'Nuevo':

                    bot.sendMessage(chat_id,'Para armar el meme del perro, tenés que mandar un mensaje con cuatro partes.\nEscribí "1." seguido del nombre del perro grande.\n"2." seguido de lo que dice el perro grande.\n"3." seguido del nombre del perro chico.\n"4." seguido de lo que dice el perro chico.\nEjemplo:\n1. Escritores antes 2. Prendan fuego toda mi obra 3. Escritores ahora 4. No me pirateen el PDF')

                # Si nos da el mensaje bien, arranca todo
                else:

                    if re.match('1.*2.*3.*4.*',update.message.text):

                        try:

                            # Separar cada frase en grupos
                            groups = re.findall(r'1.(.*)2.(.*)3.(.*)4.(.*)',update.message.text)                    

                            # Buscamos la imagen con un http request
                            img_response = requests.get('http://jmcafferata.com/misc/perros.jpg')

                            # Abrimos la imagen con PIL
                            img_original = Image.open(BytesIO(img_response.content))

                            # Creamos la imagen final
                            img_final = ImageDraw.Draw(img_original)

                            # Tipografía
                            font_response = requests.get('http://jmcafferata.com/misc/RobotoMono-Regular.ttf')
                            font = ImageFont.truetype(BytesIO(font_response.content), size=30)
                            
                            # Aca se van a pegar los textos
                            pastepoints = [[197,41],[174,538],[830,136],[804,511]]

                            # Wrap text
                            for texto1, texto2, texto3, texto4 in groups:
                                textos = [texto1, texto2, texto3, texto4]
                                i = 0
                                for texto in textos:
                                    lines = textwrap.wrap(texto, width=20)
                                    y_text = pastepoints[i][1]
                                    for line in lines:
                                        width, height = font.getsize(line)
                                        img_final.text((pastepoints[i][0], y_text), line, font=font, fill=(0,0,0))
                                        y_text += height
                                    i = i+1
                            
                            # Le damos la img_final a Telegram con BytesIO
                            bio = BytesIO()
                            bio.name = 'image.jpeg'
                            img_original.save(bio, 'JPEG')
                            bio.seek(0)

                            # Enviamos la imagen final al usuario
                            bot.send_photo(chat_id=chat_id, photo=bio)

                            bot.sendMessage(chat_id,'De nada.')
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            print(exc_type, fname, exc_tb.tb_lineno)
                            print(e)
                            bot.sendMessage(chat_id,'Algo pasó.')
                    else:
                        bot.sendMessage(chat_id,'Para crear un meme del perro, decí "nuevo".')
    return "ok"