import discord
from discord.ext import commands
from config import settings
from PIL import Image
import csv
import requests

bot = commands.Bot(command_prefix=settings['prefix'])

# Инициализация словаря
dic = {}
with open('alph.csv', encoding='utf-8-sig') as file:
    file_reader = csv.reader(file, delimiter=",")
    for row in file_reader:
        n = 0
        while n < int(row[1]) * int(row[2]) + 3:
            li = []
            i = 1
            while i < int(row[1]) * int(row[2]) + 3:
                li.append(row[i])
                i = i + 1
            dic[row[0]] = li
            n = n + 1
    print('Словарь успешно инициализирован')


@bot.command(name='emo')
async def emo(ctx, arg, meo: discord.PartialEmoji):
    print('Была введена строчка: ' + arg)
    arg = str.lower(arg)
    if meo.is_custom_emoji():
        await ctx.channel.send('Ждите...')
        url_pic = str(meo.url)
        # Скачиваем изображение png
        with open('pic.png', 'wb') as handle:
            response = requests.get(url_pic, stream=True)
            if not response.ok:
                print(response)
            for block in response.iter_content(1024):
                if not block:
                    break
                handle.write(block)

        # Открываем изображение "пиксель"
        pic = Image.open('pic.png')
        w_pic = pic.width   # Ширина изображения "пикселя"
        h_pic = pic.height  # Высота изображения "пикселя"
        width = (len(arg) - 1) * w_pic   # Начальная ширина итогового изображения
        height = 0  # Начальная высота итогового изображения
        height_cells = 0    # Высота итогового изображения в "пикселях"
        # Определяем размер итогового изображения
        for el in arg:
            if el in dic.keys():
                li2 = dic.get(el)
                width = width + (int(li2[0]) * w_pic)
                if height < int(li[1]) * h_pic:
                    height = int(li2[1]) * h_pic
                    height_cells = int(li2[1])
        result = Image.new('RGBA', (width, height), (0,0,0,0)) # Создаем итоговое пустое изображение
        # Собираем буквы в слова
        x_res = 0
        y_res = 0
        msg = await ctx.channel.send('Прогресс: 0%')
        co = 0
        for el in arg:
            if el == '_':
                x_res = x_res + w_pic
                co = co + 1
            else:
                if el in dic.keys():
                    li2 = dic.get(el)
                    w_cells = int(li2[0])   # Ширина буквы в количестве "пикселей"
                    h_cells = int(li2[1])    # Высота буквы в количестве "пикселей"
                    w_letter = w_pic * w_cells  # Ширина буквы в пикселях
                    h_letter = h_pic * h_cells  # Высота буквы в пикселях
                    letter = Image.new('RGBA', (w_letter, h_letter), (0, 0, 0, 0))   # Создаем пустое изображение буквы
                    x = 0
                    y = 0
                    n = 2

                    while n < w_cells * h_cells + 2:
                        if int(li2[n]) == 1:
                            letter.paste(pic, (x, y), pic)
                            x = x + w_pic
                        else:
                            x = x + w_pic
                        if (n - 1) % w_cells == 0:
                            y = y + h_pic
                            x = 0
                        n = n + 1

                    if h_cells < height_cells:
                        razn = height_cells - h_cells
                        y_res = y_res + razn * h_pic
                        result.paste(letter, (x_res, y_res), letter)
                        y_res = y_res - razn * h_pic
                    else:
                        result.paste(letter, (x_res, y_res), letter)
                    x_res = x_res + w_letter + w_pic
                    result.save('result.png')
                    co = co + 1
                    loading = co * 100 / len(arg)
                    await msg.edit(content='Прогресс: ' + str(loading) + '%')

                else:
                    await ctx.channel.send('Недопустимый символ!')
                    break
        else:
            await ctx.channel.send(file=discord.File('result.png')) # Вывод результата

bot.run(settings['token'])
