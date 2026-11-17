#!/usr/bin/env python3
"""Port of the kazakhstan-travel.com SEO assets to almaty-travel.kz (critique of 16.11.2026). Idempotent.

Source: seo-audit-2026-11-16/almaty-critique.md, sections 2 and 3. Only owner facts are used:
tour price = private 4x4 SUV + transport costs, English-speaking driver-guide, hotel pickup in Almaty,
park tickets and eco fees, water; meals and accommodation separate or All inclusive; since 2011,
about 700-1000 travellers a year. No prices, no Kyrgyzstan, no "licensed", no UNESCO.
Every sentence the critic marked [проверить] was dropped.

1. New titles (<=60), descriptions (<=155, also og/twitter and JSON-LD WebPage/TouristTrip/Article)
   and H1 for the EN pages of the mapping table, RU copies for the top-5 pages.
2. Top-5 pages (/en/, 1-day Charyn, 817, 2-day Altyn-Emel, private driver-guide) + RU copies:
   Highlights / drive / What to bring / FAQ sections and FAQPage JSON-LD.
3. Guide articles: internal phrases removed ("owner materials reconciled", "photographs supplied by
   the owner", "catalogue"), neutral yurt wording, full descriptions.
4. Slogan grammar, junk AI-chat markup on tours/398, TravelAgency JSON-LD (logo, foundingDate,
   contactPoint, areaServed, knowsLanguage).

Run on the review repo:  python3 tools/com_seo_port.py <repo>
build_live.py also calls apply(page_map) on the public build (after site_patches, which resets pages/26).
"""
import html
import json
import os
import re
import sys

HOST = 'https://www.almaty-travel.kz'
START, END = '<!--com-seo:start-->', '<!--com-seo:end-->'
LD = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)

ORG = {
    '@context': 'https://schema.org', '@type': 'TravelAgency', '@id': HOST + '/#organization',
    'name': 'Kazakhstan Travel', 'url': HOST + '/',
    'logo': HOST + '/assets/images/apple-touch-icon-180x180.png',
    'telephone': '+77775259885', 'email': 'kztravel@mail.ru', 'foundingDate': '2011',
    'areaServed': {'@type': 'AdministrativeArea', 'name': 'Almaty Region, Kazakhstan'},
    'knowsLanguage': ['en', 'ru'],
    'contactPoint': {'@type': 'ContactPoint', 'contactType': 'customer service', 'telephone': '+77775259885',
                     'email': 'kztravel@mail.ru', 'url': 'https://wa.me/77775259885',
                     'availableLanguage': ['English', 'Russian']},
    'sameAs': ['https://www.instagram.com/kazakhstan_travel/'],
}

SLOGAN = ('even if it is seems impossible', 'even where it seems impossible')

INCL_EN = ('The 4x4 and all transport costs, the English-speaking driver-guide, hotel pickup and drop-off, '
           'national park tickets and eco fees, and drinking water.')
INCL_RU = ('Внедорожник 4x4 и все расходы на дорогу, гид-водитель, встреча и доставка до отеля, '
           'билеты в нацпарки и экосборы, питьевая вода.')

# ---------------------------------------------------------------- top-5 content blocks
# (h2, html) sections; ('faq', [(q, a_html), ...]) is rendered as h3/p and FAQPage JSON-LD.
HOME_EN = [
    ('What the tour price includes',
     '<ul class="tour-included"><li>Private 4x4 SUV and all transport costs</li><li>English-speaking driver-guide</li>'
     '<li>Pickup and drop-off at your hotel in Almaty</li><li>National park entrance tickets and eco fees</li>'
     '<li>Drinking water</li></ul><p>Meals and accommodation are paid separately, or you can choose the '
     '<strong>All inclusive</strong> package with hotels in the national parks and meals. Prices are calculated '
     'for your dates and group: send us a message on WhatsApp.</p>'),
    ('How many days do you need?',
     '<ul><li><strong>1 day</strong>: <a href="{b}/en/private-tours/1-day-charyn/">Charyn Canyon</a>, '
     '<a href="{b}/en/tours/51/">Big Almaty Lake</a>, <a href="{b}/en/private-tours/1-day-altyn-emel-singing-dune/">'
     'Altyn-Emel Singing Dune</a>, or the long <a href="{b}/en/private-tours/1-day-kolsai-kaindy-charyn/">Kolsai, '
     'Kaindy and Charyn express</a>.</li><li><strong>2 days</strong>: <a href="{b}/en/tours/817/">Kolsai Lakes, '
     'Kaindy and Charyn</a> with a night in Saty village, or <a href="{b}/en/private-tours/2-day-altyn-emel/">'
     'Altyn-Emel</a> with a sunset on the Singing Dune.</li><li><strong>3–6 days</strong>: the '
     '<a href="{b}/en/private-tours/4-day-golden-ring-almaty/">Golden Ring</a> loop through all three national '
     'parks.</li></ul>'),
    ('faq', [
        ('Is the tour really private?', 'Yes. Only your group is in the car, with your own driver-guide. We do not run shared group tours.'),
        ('Does the guide speak English?', 'Yes, our driver-guides speak English.'),
        ('Where do you pick us up?', 'At your hotel or apartment in Almaty, and we bring you back there at the end of the tour.'),
        ('Are meals included?', 'No. Meals and accommodation are paid separately, or you can book them with the All inclusive package.'),
        ('How do I get a price?', 'Message us on WhatsApp +7 777 525 98 85 with your dates, number of travellers and the places '
                                  'you want to see. We reply with a price for your group.'),
    ]),
]
HOME_EN_INTRO = ('Kazakhstan Travel has been running private tours from Almaty since 2011. Your group travels on its own in '
                 'our 4x4 SUV with an English-speaking driver-guide, who picks you up at your hotel and plans the day around '
                 'your pace. We host about 700–1000 travellers a year, from couples to families and friends travelling '
                 'together. Every route can be changed, and we never add strangers to your car.')

HOME_RU = [
    (None, '<p>Kazakhstan Travel проводит частные туры из Алматы с 2011 года. Вы едете только своей компанией на нашем '
           'внедорожнике 4x4 с гидом-водителем: он встречает вас в отеле и строит день в вашем темпе. За год у нас бывает '
           'около 700–1000 путешественников — пары, семьи, друзья. Любой маршрут можно изменить, и мы никогда не '
           'подсаживаем к вам чужих людей.</p>'),
    ('Что входит в стоимость',
     '<ul class="tour-included"><li>Частный внедорожник 4x4 и все расходы на дорогу</li><li>Гид-водитель</li>'
     '<li>Встреча и доставка до отеля в Алматы</li><li>Входные билеты в нацпарки и экосборы</li><li>Питьевая вода</li></ul>'
     '<p>Питание и проживание — отдельно или пакетом <strong>All inclusive</strong>. Стоимость считаем под ваши даты '
     'и группу: напишите в WhatsApp.</p>'),
    ('Сколько дней нужно?',
     '<ul><li><strong>1 день</strong>: <a href="{b}/ru/private-tours/1-day-charyn/">Чарын</a>, '
     '<a href="{b}/ru/tours/51/">Большое Алматинское озеро</a>, <a href="{b}/ru/private-tours/1-day-altyn-emel-singing-dune/">'
     'Поющий бархан</a> или длинный <a href="{b}/ru/private-tours/1-day-kolsai-kaindy-charyn/">экспресс Кольсай — '
     'Каинды — Чарын</a>.</li><li><strong>2 дня</strong>: <a href="{b}/ru/tours/817/">Кольсай, Каинды и Чарын</a> '
     'с ночёвкой в Саты или <a href="{b}/ru/private-tours/2-day-altyn-emel/">Алтын-Эмель</a> с закатом на бархане.</li>'
     '<li><strong>3–6 дней</strong>: <a href="{b}/ru/private-tours/4-day-golden-ring-almaty/">«Золотое кольцо»</a> '
     'по трём нацпаркам.</li></ul>'),
    ('faq', [
        ('Тур правда частный?', 'Да, в машине только ваша группа и ваш гид-водитель.'),
        ('Где вы встречаете?', 'В вашем отеле или квартире в Алматы, туда же привозим в конце тура.'),
        ('Питание входит в стоимость?', 'Нет, питание и проживание оплачиваются отдельно или пакетом All inclusive.'),
        ('Как узнать цену?', 'Напишите в WhatsApp +7 777 525 98 85 даты, сколько вас и куда хотите поехать — пришлём стоимость для вашей группы.'),
    ]),
]

CHARYN_EN = [
    ('Highlights',
     '<ul><li>The Valley of Castles, where wind and water have cut the rock into towers and walls</li>'
     '<li>Viewpoints over the canyon rim and the Charyn River</li>'
     '<li>Time for photos at your own pace, with no group to wait for</li></ul>'),
    ('How long is the drive and how much walking?',
     '<p>The drive from Almaty to Charyn takes about 3.5 hours each way (a little longer with the market stop), so it is '
     'a full day out. Walking is up to you: you can stay near the viewpoints or walk down through the Valley of Castles '
     'towards the river. Tell us about children, older travellers or knee problems, and the driver-guide will plan an '
     'easier route.</p>'),
    ('What to bring',
     '<p>Comfortable closed shoes with a good grip, a hat, sunglasses and sunscreen (there is little shade in the canyon), '
     'a light jacket for spring and autumn mornings, and some cash for lunch and souvenirs. Drinking water is provided '
     'in the car.</p>'),
    ('faq', [
        ('Can I visit Charyn Canyon in one day from Almaty?', 'Yes. This tour leaves at 9:00 and returns around 19:00.'),
        ('Is this a group tour?', 'No. It is a private tour for your group only, with your own driver-guide.'),
        ('What is included?', INCL_EN + ' Meals are paid separately or included in the All inclusive package.'),
        ('Is Charyn suitable for children?', 'Yes. The walk can be as short or as long as you like.'),
        ('Can I add Kolsai and Kaindy lakes?', 'Yes: in one long day on the <a href="{b}/en/private-tours/1-day-kolsai-kaindy-charyn/">'
                                               'express tour</a> or more comfortably in <a href="{b}/en/tours/817/">two days</a>.'),
        ('Is Charyn open in winter?', 'Yes, the canyon is open all year. Winter trips depend on weather and road conditions.'),
    ]),
]
CHARYN_RU = [
    ('Главное',
     '<ul><li>Долина замков: ветер и вода вырезали в скалах башни и стены</li>'
     '<li>Смотровые площадки над каньоном и рекой Чарын</li><li>Фото в своём темпе, без ожидания группы</li></ul>'),
    ('Дорога и прогулка',
     '<p>Дорога в одну сторону — около 3,5 часа (с остановкой на рынке дольше), поэтому это целый день. Сколько гулять, '
     'решаете вы. Если в группе дети или пожилые, скажите заранее, и гид-водитель предложит маршрут полегче.</p>'),
    ('Что взять',
     '<p>Удобную закрытую обувь, головной убор, очки и крем от солнца (тени в каньоне мало), лёгкую куртку весной и осенью, '
     'наличные на обед. Воду даём в машине.</p>'),
    ('faq', [
        ('Можно ли съездить на Чарын за один день?', 'Да, выезд в 9:00, возвращение около 19:00.'),
        ('Это групповой тур?', 'Нет, в машине только ваша группа и ваш гид-водитель.'),
        ('Что входит в стоимость?', INCL_RU + ' Питание — отдельно или пакетом All inclusive.'),
        ('Подходит ли тур детям?', 'Да, прогулка может быть короткой или длинной — как вам удобно.'),
        ('Можно добавить Кольсай и Каинды?', 'Да: за один длинный день в <a href="{b}/ru/private-tours/1-day-kolsai-kaindy-charyn/">'
                                             'экспресс-туре</a> или спокойнее — в <a href="{b}/ru/tours/817/">туре на 2 дня</a>.'),
        ('Каньон открыт зимой?', 'Да, круглый год. Зимой поездка зависит от погоды и дорог.'),
    ]),
]

T817_EN = [
    ('Where you stay',
     '<p>The night is spent in Saty village, in a guesthouse or a <a href="{b}/en/pages/47.html">yurt</a>. Accommodation '
     'and meals are paid separately or booked as the All inclusive package; tell us which you prefer.</p>'),
    ('What to bring',
     '<p>Walking shoes for the canyon and the Kaindy trail, a warm layer for the evening at the lakes (Kolsai and Kaindy '
     'are higher and cooler than Almaty), a hat and sunscreen for Charyn, a small backpack and an overnight bag.</p>'),
    ('faq', [
        ('Why two days instead of one?', 'The one-day express starts at 6:00 and ends around 23:00. With two days you have '
                                         'time to walk at each place and arrive in daylight.'),
        ('How hard is the walking?', 'The canyon descent is 2.5 km downhill; you return by local transport. The Kaindy trail '
                                     'is about 3 km each way, or you can ride a horse.'),
        ('Can we stay in a yurt?', 'Yes, yurt stays near Kolsai can be arranged for the night in Saty.'),
        ('What is included?', INCL_EN + ' Accommodation and meals are separate or All inclusive.'),
        ('Can we add Altyn-Emel?', 'Yes: see the <a href="{b}/en/private-tours/3-day-altyn-emel-charyn-kolsai-kaindy/">'
                                   '3-day Golden Ring Express</a>.'),
    ]),
]
T817_RU = [
    ('Проживание',
     '<p>Ночёвка в селе Саты — в гостевом доме или <a href="{b}/ru/pages/47.html">юрте</a>. Проживание и питание — '
     'отдельно или пакетом All inclusive.</p>'),
    ('Что взять',
     '<p>Удобную обувь, тёплую кофту на вечер у озёр, головной убор и крем от солнца для Чарына, рюкзак и вещи на ночь.</p>'),
    ('faq', [
        ('Почему не за один день?', 'Экспресс идёт с 6:00 до 23:00, а за два дня есть время погулять в каждом месте.'),
        ('Сложно ли идти пешком?', 'Спуск в каньон — 2,5 км, обратно на местном транспорте. К озеру Каинды — около 3 км пешком или верхом.'),
        ('Можно ночевать в юрте?', 'Да, ночёвку в юрте в Саты можно организовать.'),
        ('Можно добавить Алтын-Эмель?', 'Да — <a href="{b}/ru/private-tours/3-day-altyn-emel-charyn-kolsai-kaindy/">'
                                        '«Золотое кольцо» экспресс на 3 дня</a>.'),
    ]),
]

AE_EN = [
    ('Highlights',
     '<ul><li>The Singing Dune: a huge sand dune that hums in dry, windy weather</li>'
     '<li>The Aktau mountains: layered white, red and ochre hills</li>'
     '<li>Steppe views with a chance to see wildlife such as gazelles and kulans</li></ul>'),
    ('What to bring',
     '<p>In summer the park is hot and has no shade: bring a hat, sunglasses, sunscreen and light long sleeves. Wear shoes '
     'you can climb sand in. Evenings and spring/autumn mornings can be windy and cool, so pack a warm layer.</p>'),
    ('faq', [
        ('Can I see Altyn-Emel in one day?', 'Yes, see the <a href="{b}/en/private-tours/1-day-altyn-emel-singing-dune/">Singing '
                                             'Dune day trip</a> or the <a href="{b}/en/private-tours/1-day-altyn-emel-full-park/">'
                                             'full-day Aktau and Singing Dune</a>. The two-day tour is less rushed and includes '
                                             'sunset at the dune.'),
        ('How long is the drive from Almaty?', 'About four hours each way.'),
        ('Where do we sleep?', 'In a guesthouse in Basshi village. Accommodation and meals are paid separately or booked as '
                               'the All inclusive package.'),
        ('Is the dune climb difficult?', 'It is steep soft sand; take your time. You can also watch from the bottom.'),
        ('What is included?', INCL_EN),
        ('Can I combine Altyn-Emel with Charyn and Kolsai?',
         'Yes, on the <a href="{b}/en/private-tours/3-day-altyn-emel-charyn-kolsai-kaindy/">3-day Golden Ring Express</a> '
         'or the <a href="{b}/en/private-tours/4-day-golden-ring-almaty/">4-day Golden Ring</a>.'),
    ]),
]
AE_RU = [
    ('Главное',
     '<ul><li>Поющий бархан: огромная песчаная дюна, которая гудит в сухую ветреную погоду</li>'
     '<li>Горы Актау: полосатые белые, красные и охристые холмы</li>'
     '<li>Степные виды и шанс увидеть джейранов и куланов</li></ul>'),
    ('Что взять',
     '<p>Летом в парке жарко и нет тени — головной убор, очки, крем от солнца, лёгкая одежда с длинным рукавом, обувь для '
     'песка. Вечером, весной и осенью бывает ветрено и прохладно — возьмите тёплую кофту.</p>'),
    ('faq', [
        ('Можно ли за один день?', 'Да, есть однодневные программы: <a href="{b}/ru/private-tours/1-day-altyn-emel-singing-dune/">'
                                   'Поющий бархан</a> и <a href="{b}/ru/private-tours/1-day-altyn-emel-full-park/">Актау и бархан</a>, '
                                   'но без заката на бархане.'),
        ('Сколько ехать из Алматы?', 'Около 4 часов в одну сторону.'),
        ('Где ночуем?', 'В гостевом доме в селе Басши. Проживание и питание — отдельно или пакетом All inclusive.'),
        ('Можно объединить с Чарыном и Кольсаем?', 'Да — <a href="{b}/ru/private-tours/3-day-altyn-emel-charyn-kolsai-kaindy/">'
                                                   '«Золотое кольцо» на 3 дня</a> или <a href="{b}/ru/private-tours/4-day-golden-ring-almaty/">'
                                                   'на 4 дня</a>.'),
    ]),
]

DG_EN = [
    ('Driver-guide or a full private tour?',
     '<p>A <strong>driver-guide</strong> drives our 4x4 and also shows you the places: he knows the roads, the trails and the '
     'best viewpoints, and speaks English. You can book him for one of our ready routes, for your own route, or simply as '
     'transport with a driver. A <strong>private tour</strong> is the same car and driver-guide plus a planned programme and, '
     'if you like, booked hotels and meals (All inclusive). Either way, only your group is in the car.</p>'),
    ('When a driver-guide is the best choice',
     '<ul><li>You want to set your own pace and stops, for example for photography</li>'
     '<li>You travel with children or older relatives and need a flexible day</li>'
     '<li>You are combining several places, such as Charyn, Kolsai and Altyn-Emel, over a few days</li>'
     '<li>You want local help with park tickets, roads and timing</li></ul>'),
    ('faq', [
        ('Does the driver-guide speak English?', 'Yes.'),
        ('Is fuel included?', 'Yes. The price includes the car and all transport costs, the driver-guide, park tickets and '
                              'eco fees, water and hotel pickup.'),
        ('Do I need an SUV for Kolsai and Kaindy?', 'The roads to the lakes include mountain and gravel sections, which is why '
                                                    'we use 4x4 vehicles.'),
        ('Can the driver-guide stay with us for several days?', 'Yes, for multi-day routes such as the '
                                                                '<a href="{b}/en/private-tours/4-day-golden-ring-almaty/">Golden Ring</a>.'),
        ('Can we change the route on the day?', 'Within reason, yes: discuss it with your driver-guide. Big changes are best '
                                                'agreed in advance on WhatsApp.'),
        ('Are meals and hotels included?', 'No, they are paid separately or booked as the All inclusive package.'),
    ]),
]
DG_RU = [
    ('Водитель-гид или полноценный тур?',
     '<p><strong>Водитель-гид</strong> ведёт наш внедорожник и одновременно показывает места: знает дороги, тропы и лучшие '
     'точки. Его можно заказать на готовый маршрут, на свой маршрут или просто как транспорт с водителем. '
     '<strong>Частный тур</strong> — та же машина и гид плюс готовая программа и, по желанию, отели и питание (All inclusive). '
     'В обоих случаях в машине только ваша группа.</p>'),
    ('Когда это удобнее всего',
     '<ul><li>Вы хотите свой темп и остановки, например для фото</li><li>Едете с детьми или пожилыми родственниками</li>'
     '<li>Объединяете несколько мест за несколько дней</li><li>Нужна помощь с билетами, дорогами и временем</li></ul>'),
    ('faq', [
        ('Топливо входит?', 'Да: машина и все расходы на дорогу, гид-водитель, билеты и экосборы, вода, встреча в отеле.'),
        ('Нужен ли внедорожник на Кольсай?', 'На дороге к озёрам есть горные и грунтовые участки, поэтому мы ездим на 4x4.'),
        ('Может гид-водитель быть с нами несколько дней?', 'Да, например в туре <a href="{b}/ru/private-tours/4-day-golden-ring-almaty/">'
                                                           '«Золотое кольцо»</a>.'),
        ('Питание и отели входят?', 'Нет, отдельно или пакетом All inclusive.'),
    ]),
]
CARS = {'en': 'We use our own 4x4 SUVs, suitable for mountain and gravel roads to the lakes and national parks.',
        'ru': 'Мы ездим на собственных внедорожниках 4x4: они подходят для горных и грунтовых дорог к озёрам и нацпаркам.'}

# ---------------------------------------------------------------- meta per page (key = path without summer/)
P = {}


def page(key, title, desc, h1=None, block=None, anchor='cta'):
    assert len(title) <= 60, (key, len(title))
    assert len(desc) <= 155, (key, len(desc))
    P[key] = dict(title=title, desc=desc, h1=h1, block=block, anchor=anchor)


page('en/index.html', 'Private Tours from Almaty with a Driver-Guide',
     'Private 4x4 tours from Almaty since 2011: Charyn Canyon, Kolsai and Kaindy lakes, Altyn-Emel. English-speaking driver-guide, hotel pickup, park fees.',
     'Private Tours from Almaty with an English-Speaking Driver-Guide', HOME_EN, 'home')
page('ru/index.html', 'Частные туры из Алматы с гидом-водителем',
     'Частные туры на внедорожнике 4x4 из Алматы с 2011 года: Чарын, Кольсай и Каинды, Алтын-Эмель. Гид-водитель, встреча в отеле, билеты в парки включены.',
     'Частные туры из Алматы с гидом-водителем', HOME_RU, 'home')
P['index.html'] = P['ru/index.html']  # stale root copy (the live build replaces it with ru/index.html)
page('en/private-tours/1-day-charyn/index.html', 'Private Charyn Canyon Tour from Almaty (1 Day)',
     'Private day trip from Almaty to Charyn Canyon and the Valley of Castles by 4x4 with an English-speaking driver-guide. Hotel pickup and park fees included.',
     'Charyn Canyon Private Day Tour from Almaty', CHARYN_EN)
page('ru/private-tours/1-day-charyn/index.html', 'Частный тур на Чарынский каньон из Алматы — 1 день',
     'Частная поездка из Алматы на Чарынский каньон и Долину замков на внедорожнике 4x4 с гидом-водителем. Встреча в отеле, билеты в парк и вода включены.',
     'Чарынский каньон — частный тур на 1 день из Алматы', CHARYN_RU)
page('en/tours/817/index.html', 'Kolsai Lakes & Charyn Canyon Tour: 2-Day Private Trip',
     'Two-day private tour from Almaty: Charyn Canyon, Kolsai Lake, Kaindy sunken forest and Black Canyon, night in Saty. 4x4, English-speaking driver-guide.',
     'Kolsai Lakes, Kaindy and Charyn Canyon — 2-Day Private Tour from Almaty', T817_EN)
page('ru/tours/817/index.html', 'Кольсай, Каинды и Чарын — частный тур на 2 дня',
     'Частный тур из Алматы на 2 дня: Чарынский каньон, озёра Кольсай и Каинды, Чёрный каньон, ночёвка в Саты. Внедорожник 4x4 и гид-водитель.',
     'Кольсай, Каинды и Чарынский каньон — частный тур на 2 дня из Алматы', T817_RU)
page('en/private-tours/2-day-altyn-emel/index.html', 'Altyn-Emel Tour from Almaty: 2-Day Private Trip',
     'Two-day private Altyn-Emel tour from Almaty: Singing Dune at sunset, Aktau mountains, 700-year-old willow, night in Basshi. 4x4 and driver-guide.',
     'Altyn-Emel National Park — 2-Day Private Tour from Almaty', AE_EN)
page('ru/private-tours/2-day-altyn-emel/index.html', 'Тур в Алтын-Эмель из Алматы — частный, 2 дня',
     'Частный тур в Алтын-Эмель на 2 дня: закат на Поющем бархане, горы Актау, 700-летняя ива, ночёвка в Басши. Внедорожник 4x4 и гид-водитель.',
     'Национальный парк Алтын-Эмель — частный тур на 2 дня из Алматы', AE_RU)
page('en/pages/26.html', 'Private Driver-Guide in Almaty with a 4x4',
     'Hire a private English-speaking driver-guide in Almaty with a 4x4: day trips, multi-day routes or transport only. Fuel, park fees and water included.',
     'Private Driver-Guide in Almaty', DG_EN)
page('ru/pages/26.html', 'Частный водитель-гид в Алматы на внедорожнике 4x4',
     'Частный водитель-гид в Алматы на нашем внедорожнике 4x4: однодневные поездки, туры на несколько дней или только транспорт. Топливо и билеты включены.',
     'Частный водитель-гид в Алматы', DG_RU)
# meta only (EN is the main version)
page('en/private-tours/1-day-kolsai-kaindy-charyn/index.html', 'Kolsai, Kaindy & Charyn in One Day: Private Tour',
     'One long private day from Almaty (06:00–23:00): Kaindy sunken forest, Kolsai Lake and Charyn Canyon in the evening. 4x4 and English-speaking driver-guide.',
     'Kolsai, Kaindy and Charyn Canyon in One Day — Private Express Tour')
page('en/tours/54/index.html', 'Kolsai Lakes: Private Tours from Almaty',
     'Kolsai Lakes near Saty village: photos and private 1-day or 2-day tours from Almaty with Kaindy and Charyn, by 4x4 with an English-speaking driver-guide.',
     'Kolsai Lakes — Private Tours from Almaty')
page('en/tours/58/index.html', 'Kaindy Lake: Sunken Forest Tours from Almaty',
     'Kaindy Lake, the sunken spruce forest near Saty: photos and private 1–2 day tours from Almaty with Kolsai and Charyn, by 4x4 with a driver-guide.',
     'Kaindy Lake — the Sunken Forest')
page('en/tours/57/index.html', 'Charyn Canyon: Valley of Castles and Ash Grove',
     'Charyn Canyon near Almaty: the Valley of Castles and a relict ash grove of about 5,000 hectares. Photos and private tours from Almaty with a driver-guide.',
     'Charyn Canyon: Valley of Castles and Ash Grove')
page('en/private-tours/3-day-kolsai-camping/index.html', 'Kolsai Lakes Camping Tour: 3 Days with Charyn & Kaindy',
     'Three-day private tour from Almaty with a tent night at Kolsai Lake 2, Kaindy Lake and Charyn Canyon. 4x4 and English-speaking driver-guide.',
     'Charyn, Kaindy and Kolsai Lakes — 3-Day Camping Tour')
page('en/private-tours/3-day-charyn-kolsai-kaindy/index.html', 'Charyn, Kolsai & Kaindy: 3-Day Private Tour',
     'A slower three-day private tour from Almaty: Kaindy and Kolsai lakes, the Black and Moon canyons and a sunset walk in Charyn Canyon. 4x4 and driver-guide.',
     'Charyn, Kolsai and Kaindy — 3-Day Private Tour')
page('en/private-tours/3-day-kolsai-hiking/index.html', 'Kolsai Lakes Hiking Tour: 3 Days from Almaty',
     'Three-day private hiking tour from Almaty: Kolsai Lake 1 to 2 trail, Kaindy Lake and Charyn Canyon with an English-speaking driver-guide and 4x4.',
     'Kolsai Lakes Hiking Tour with Charyn and Kaindy — 3 Days')
page('en/private-tours/1-day-altyn-emel-singing-dune/index.html', 'Altyn-Emel Day Trip from Almaty: Singing Dune',
     'Private day trip from Almaty to the Singing Dune in Altyn-Emel National Park by 4x4 with an English-speaking driver-guide. Hotel pickup, park fees.',
     'Altyn-Emel Singing Dune — Private Day Trip from Almaty')
page('en/private-tours/1-day-altyn-emel-full-park/index.html', 'Altyn-Emel in One Day: Aktau and Singing Dune',
     'A full private day in Altyn-Emel from Almaty: the Aktau mountains and the Singing Dune by 4x4 with an English-speaking driver-guide. Early start.',
     'Altyn-Emel in One Day: Aktau Mountains and the Singing Dune')
page('en/tours/379/index.html', 'Altyn-Emel National Park: Tours from Almaty',
     'Altyn-Emel National Park: the Singing Dune, the Aktau mountains and Basshi village. Compare private 1-day, 2-day and 3-day tours from Almaty.',
     'Altyn-Emel National Park — Tour Options')
page('en/private-tours/3-day-altyn-emel-charyn-kolsai-kaindy/index.html', 'Golden Ring Express: 3-Day Private Tour from Almaty',
     'Three-day private loop from Almaty: Kolsai and Kaindy lakes, Charyn Canyon, Singing Dune and Aktau in Altyn-Emel. 4x4 and English-speaking driver-guide.',
     'Golden Ring Express — Kolsai, Charyn and Altyn-Emel in 3 Days')
page('en/private-tours/4-day-golden-ring-almaty/index.html', 'Golden Ring Tour from Almaty: 4 Days, Private 4x4',
     'Four-day private loop from Almaty through Altyn-Emel, Charyn Canyon, Kolsai and Kaindy lakes with an English-speaking driver-guide and hotel pickup.',
     'Golden Ring of Almaty Region — 4-Day Private Tour')
page('en/private-tours/6-day-golden-ring/index.html', 'Golden Ring with Assy Plateau: 6-Day Private Tour',
     'Six-day private tour from Almaty: Altyn-Emel, Charyn, Kolsai, Kaindy and the Assy plateau with an English-speaking driver-guide and 4x4.',
     'Golden Ring with the Assy Plateau — 6-Day Private Tour')
page('en/tours/51/index.html', 'Big Almaty Lake Tour from Almaty: Private Day Trip',
     'Private trip from Almaty to Big Almaty Lake through the Big Almaty Gorge, optional Sunkar falconry centre. 4x4 and English-speaking driver-guide.',
     'Big Almaty Lake — Private Tour from Almaty')
page('en/tours/55/index.html', 'Issyk Lake & Turgen Gorge Day Trip from Almaty',
     'Private day trip from Almaty to the Bear waterfall in Turgen Gorge and to Issyk Lake by 4x4 with an English-speaking driver-guide. Trout farm lunch stop.',
     'Issyk Lake and Turgen Gorge — Private Day Trip')
page('en/private-tours/tamgaly-tas/index.html', 'Tamgaly-Tas Petroglyphs Day Trip from Almaty',
     'Private day trip from Almaty to the Tamgaly-Tas rock carvings on the Ili River, past Kapchagay lake. 4x4, English-speaking driver-guide, hotel pickup.',
     'Tamgaly-Tas — Petroglyphs on the Ili River, Private Trip')
page('en/tours/50/index.html', 'Almaty City Tour: Private Sightseeing with a Guide',
     'Private Almaty city tour with an English-speaking guide: Panfilov Park, the Green Bazaar, a museum, Shymbulak and Kok-Tobe, with hotel pickup.',
     'Almaty City Tour — Private Sightseeing Day')
page('en/private-tours/helicopter-flight/index.html', 'Helicopter Flights in Almaty: Mountains & Lakes',
     'Private helicopter flights near Almaty over the mountains to Big Almaty Lake, Charyn Canyon or Kolsai. Send your date and group size on WhatsApp.',
     'Helicopter Flights over Almaty Mountains')
page('en/private-tours/airplane-flight/index.html', 'Scenic Light Aircraft Flights near Almaty',
     'Scenic light aircraft flights near Almaty over the city, Eight Lakes, Turgen, Charyn and the Singing Dune, for up to 3 passengers. Ask on WhatsApp.',
     'Light Aircraft Flights near Almaty')
page('en/pages/319.html', 'Horse Riding near Almaty: Private Mountain Rides',
     'Private horse riding in the mountains near Almaty from Medeu gorge: rides of 2 to 6 hours to waterfalls, lakes and viewpoints with a guide.',
     'Horse Riding in the Mountains near Almaty')
page('en/pages/20.html', 'Buggy & ATV Tours near Almaty',
     'Buggy and ATV routes near Almaty: 1 to 3 hours on paved roads or off-road, including Big Almaty Lake, with instruction and a guide.',
     'Buggy and ATV Routes near Almaty')
page('en/pages/47.html', 'Yurt Stay at Kolsai Lakes: Overnight near Saty',
     'Stay overnight in a yurt near the Kolsai Lakes on a private tour from Almaty, combined with Kolsai, Kaindy and Charyn Canyon. Send your dates on WhatsApp.',
     'Yurt Stays near Kolsai Lakes')
page('en/tours/index.html', 'Private Day Trips and Tours from Almaty',
     'All private tours from Almaty in one place: day trips to Charyn, Kolsai, Big Almaty Lake, Altyn-Emel and 2–6 day loops with a driver-guide.',
     'Private Day Trips and Tours from Almaty')
page('en/pages/13.html', 'About Kazakhstan Travel: Private Tours Since 2011',
     'Kazakhstan Travel has run private 4x4 tours from Almaty since 2011, about 700–1000 travellers a year. Own SUVs, English-speaking driver-guides.')
page('en/pages/15.html', 'Contact Kazakhstan Travel: WhatsApp +7 777 525 98 85',
     'Message Kazakhstan Travel on WhatsApp +7 777 525 98 85 or email kztravel@mail.ru with your dates, group size and route. We reply with a tailored price.')
page('en/tours/398/index.html', 'Ak Bulak ski resort | Kazakhstan Travel',
     'Ak Bulak mountain resort near Almaty: skiing, snowboarding and snow tubing in winter; mountain biking, quad bikes, horse riding and picnics in summer.')
page('ru/tours/398/index.html', 'Ак Булак | Kazakhstan Travel',
     'Курорт Ак Булак в горах Заилийского Алатау: зимой лыжи, сноуборд и тюбинг, летом горные велосипеды, квадроциклы, конные прогулки и пикники.')

# ---------------------------------------------------------------- guide articles
SOURCE_P = {
    'en': '<p class="guide-meta">Source: Kazakhstan Travel itineraries and owner materials reconciled on 28 October 2026. '
          'Linked programmes are available above; photographs were supplied by the owner. Availability, weather and '
          'individual arrangements require confirmation.</p>',
    'ru': '<p class="guide-meta">Источник: программы Kazakhstan Travel и материалы владельца, сверенные 28 октября 2026. '
          'Программы доступны по ссылкам выше; фотографии предоставлены владельцем. Доступность, погода и индивидуальные '
          'условия требуют подтверждения.</p>',
}
G = {}  # guide slug/lang -> dict(sub=[(old, new)], title, desc, h1)
G_EN_COMMON = [('<h2>Itineraries and source information</h2>', '<h2>Related private tours</h2>'),
               ('alt="Yurt photograph supplied by the owner"', 'alt="Yurt near the Kolsai lakes"')]
G_RU_COMMON = [('<h2>Программы и первичные материалы</h2>', '<h2>Частные туры по теме</h2>'),
               ('alt="Юрта: фотография, предоставленная владельцем"', 'alt="Юрта у озёр Кольсай"')]
G['en/guide/booking-private-tour-from-almaty/index.html'] = dict(
    title='How to Book a Private Tour from Almaty | Kazakhstan Travel',
    desc='How to get a price for a private tour from Almaty: send dates, group size and route on WhatsApp. What the price includes and what is paid separately.',
    h1='How to Book a Private Tour from Almaty',
    sub=[('Send the manager your dates, party size, preferred destinations and available time. Prices are not published on '
          'the website: the price and services are confirmed for your request.',
          'Send us your dates, group size, the places you want to see and how much time you have. We reply on WhatsApp with '
          'a price for your group.'),
         ('Confirm the guide-driver’s language if you need English-speaking assistance. An English-speaking guide-driver and '
          'a separate interpreter are different services.',
          'Our driver-guides speak English. A separate interpreter is a different service.'),
         ('Which arrangements should you confirm?', 'What does the price include?'),
         ('Ask for a list of transport, guiding, entrance fees, meals, accommodation and optional activities included in your '
          'particular proposal. Discuss payment, cancellation and possible itinerary changes. This article does not establish '
          'new booking terms.',
          'The tour price includes the private 4x4 SUV and all transport costs, an English-speaking driver-guide, hotel pickup '
          'and drop-off in Almaty, national park tickets and eco fees, and drinking water. Meals and accommodation are paid '
          'separately or booked as the All inclusive package. Discuss payment, cancellation and possible route changes '
          'before you confirm.'),
         ('The manager can discuss a route and availability for your dates. Start by comparing the existing catalogue; '
          'availability and final arrangements require confirmation.',
          'We can plan a route around your dates and interests, or adapt one of our ready-made tours.'),
         ('>Tour catalogue<', '>All private tours from Almaty<')])
G['en/guide/charyn-walking-and-day-trip/index.html'] = dict(
    desc='Charyn Canyon as a day trip from Almaty or combined with the Kolsai and Kaindy lakes: how the tours differ and how much walking to expect.',
    sub=[('Choose between a dedicated Charyn day trip and itineraries combining the canyon with the lakes. Walking time and '
          'effort depend on the programme; there is no single walking distance for every tour.',
          'Charyn Canyon as a day trip from Almaty or combined with the Kolsai and Kaindy lakes: how the tours differ and '
          'how much walking to expect.'),
         ('This applies to that itinerary, not automatically to every trip. Confirm your own walking section and return transport.',
          'On other tours the walking part can be shorter or longer: tell us how much you want to walk.'),
         ('Ask about the forecast and route conditions for your date. Useful points to discuss include suitable footwear, sun '
          'protection, drinking water and clothing for the weather.',
          'Wear comfortable closed shoes and bring a hat and sun protection; drinking water is provided in the car. Check the '
          'forecast for your date and dress for the weather.')])
G['en/guide/kolsai-kaindy-one-or-two-days/index.html'] = dict(
    title='Kolsai Lakes from Almaty: 1-Day or 2-Day Tour?',
    desc='Compare a one-day and two-day private Kolsai Lakes tour from Almaty: driving time, Kaindy and Charyn stops, overnight in Saty, who each suits.',
    h1='Kolsai and Kaindy from Almaty: One Day or Two?',
    sub=[('Both options are available in the catalogue. The one-day express', 'The one-day express'),
         ('The two-day itinerary splits the journey and includes an overnight stop in Saty.',
          'The two-day tour splits the journey with a night in Saty village.'),
         (' Treat the times as itinerary guidance and confirm arrangements for your travel date.', ''),
         ('Confirm the accommodation and booking conditions when discussing the trip.',
          'You stay in a guesthouse or a yurt; accommodation and meals are paid separately or booked as the All inclusive package.'),
         ('Prices are provided by the manager rather than published on the website.', 'We reply with a price for your group.')])
G['en/guide/yurt-stay-kolsai/index.html'] = dict(
    desc='We arrange yurt stays near the Kolsai lakes on private tours from Almaty. Send your dates, and we confirm the location and facilities of your yurt.',
    sub=[('The company offers yurt accommodation in the Kolsai area. The website shows photographs supplied by the owner. '
          'Confirm the exact location, facilities and availability for your dates before booking.',
          'We arrange yurt stays near the Kolsai lakes on private tours from Almaty. Send your dates, and we confirm the '
          'location and facilities of your yurt.'),
         ('The yurt section concerns the Kolsai area. This does not mean every yurt is on the lakeshore: confirm the exact '
          'location and driving arrangements separately.',
          'Not every yurt stands on the lakeshore, so we tell you the exact location and driving time when we plan your trip.'),
         ('What do the photographs establish?', 'What are the yurts like?'),
         ('<p>The pictures introduce the accommodation but do not establish heating, a private bathroom, bed capacity or meal '
          'arrangements. Ask which facilities apply to the particular accommodation offered to you.</p>',
          '<p>Photos of the yurt camp are on our <a href="{b}/en/pages/47.html">yurt stays page</a>. Tell us what matters to '
          'you, such as the bathroom, heating, number of beds or meals, and we will confirm the details for your dates.</p>'),
         ('The pictures introduce the accommodation but do not establish heating, a private bathroom, bed capacity or meal '
          'arrangements. Ask which facilities apply to the particular accommodation offered to you.',
          'Photos of the yurt camp are on our yurt stays page. Tell us what matters to you, such as the bathroom, heating, '
          'number of beds or meals, and we will confirm the details for your dates.'),
         ('Tell the manager whether you prefer a yurt or another accommodation type, and ask for the agreed arrangements to be '
          'included in the proposal.',
          'Tell us whether you prefer a yurt or a guesthouse, and we will include it in your tour plan.')])
G['ru/guide/booking-private-tour-from-almaty/index.html'] = dict(
    title='Как заказать частный тур из Алматы | Kazakhstan Travel',
    desc='Напишите нам в WhatsApp даты, сколько вас, какие места хотите увидеть и сколько у вас времени — мы пришлём стоимость для вашей группы.',
    sub=[('Чтобы получить предложение, сообщите менеджеру даты, число участников, желаемые места и доступное время. '
          'Публичных цен на сайте нет: стоимость и состав поездки подтверждаются индивидуально.',
          'Напишите нам в WhatsApp даты, сколько вас, какие места хотите увидеть и сколько у вас времени — мы пришлём '
          'стоимость для вашей группы.'),
         ('Для английского сопровождения отдельно подтвердите язык гида-водителя. Англоговорящий гид-водитель и отдельный '
          'переводчик — разные услуги.',
          'Наши гиды-водители говорят по-английски. Отдельный переводчик — это другая услуга.'),
         ('Какие условия стоит подтвердить?', 'Что входит в стоимость?'),
         ('Попросите перечислить транспорт, сопровождение, входные билеты, питание, проживание и дополнительные активности, '
          'которые входят именно в ваше предложение. Также согласуйте оплату, отмену и возможные изменения маршрута. На этой '
          'странице не устанавливаются новые условия бронирования.',
          'В стоимость тура входят частный внедорожник 4x4 и все расходы на дорогу, гид-водитель, встреча и доставка до отеля '
          'в Алматы, входные билеты в нацпарки и экосборы, питьевая вода. Питание и проживание оплачиваются отдельно или '
          'пакетом All inclusive. Оплату, отмену и изменения маршрута обсудите до подтверждения.'),
         ('Менеджер поможет обсудить программу и возможность поездки на выбранные даты. Для начала сравните готовые маршруты '
          'в каталоге; доступность и детали подтверждаются при обращении.',
          'Мы составим маршрут под ваши даты и интересы или изменим один из готовых туров.'),
         ('>Каталог экскурсий<', '>Все частные туры из Алматы<')])
G['ru/guide/charyn-walking-and-day-trip/index.html'] = dict(
    desc='Чарын можно увидеть за один день из Алматы или вместе с озёрами Кольсай и Каинды. Сколько идти пешком, зависит от выбранного тура.',
    sub=[('У компании есть отдельная однодневная поездка в Чарын и комбинированные программы с озёрами. Время на прогулку '
          'и нагрузка зависят от выбранного маршрута — единого пешего расстояния для всех туров нет.',
          'Чарын можно увидеть за один день из Алматы или вместе с озёрами Кольсай и Каинды. Сколько идти пешком, зависит '
          'от выбранного тура.'),
         ('Это описание конкретной программы, а не обещание одинаковой логистики во всех поездках. Для своего тура отдельно '
          'подтвердите пеший участок и обратный транспорт.',
          'В других турах пеший участок может быть короче или длиннее — скажите, сколько вы хотите гулять.'),
         ('Уточните прогноз и состояние маршрута на вашу дату. Практически полезно обсудить удобную обувь, защиту от солнца, '
          'воду и одежду по погоде.',
          'Наденьте удобную закрытую обувь, возьмите головной убор и крем от солнца; питьевая вода есть в машине. '
          'Проверьте прогноз и оденьтесь по погоде.')])
G['ru/guide/kolsai-kaindy-one-or-two-days/index.html'] = dict(
    desc='Однодневный экспресс объединяет Каинды, Кольсай и Чарын с ранним выездом и поздним возвращением. Два дня — с ночёвкой в Саты.',
    sub=[('В каталоге есть оба формата. Однодневная экспресс-программа объединяет Каинды, Кольсай и Чарын с ранним выездом '
          'и поздним возвращением. Два дня позволяют распределить поездку и включают ночёвку в Саты.',
          'Однодневный экспресс объединяет Каинды, Кольсай и Чарын с ранним выездом и поздним возвращением. Два дня — с '
          'ночёвкой в Саты.'),
         (' Время служит ориентиром программы; детали нужно согласовать для выбранной даты.', ''),
         ('Ночёвка позволяет разделить маршрут на два дня, но состав размещения и условия бронирования нужно проверить при '
          'согласовании.',
          'Ночёвка — в гостевом доме или юрте; проживание и питание оплачиваются отдельно или пакетом All inclusive.'),
         ('Цена на сайте не публикуется — расчёт предоставит менеджер.', 'Мы пришлём стоимость для вашей группы.')])
G['ru/guide/yurt-stay-kolsai/index.html'] = dict(
    desc='Мы организуем проживание в юртах у озёр Кольсай в частных турах из Алматы. Напишите даты — подтвердим место и удобства вашей юрты.',
    sub=[('Компания предлагает проживание в юртах в направлении Кольсая. На сайте показаны фотографии, предоставленные '
          'владельцем. Точную площадку, условия проживания и доступность на даты нужно подтвердить перед бронированием.',
          'Мы организуем проживание в юртах у озёр Кольсай в частных турах из Алматы. Напишите даты — подтвердим место и '
          'удобства вашей юрты.'),
         ('Раздел юрт относится к направлению Кольсая. Это не означает, что любая юрта расположена прямо у берега озера: '
          'точное место и переезды нужно согласовать отдельно.',
          'Не каждая юрта стоит прямо у берега озера, поэтому точное место и время в пути мы сообщаем при планировании поездки.'),
         ('Что можно понять по фотографиям?', 'Как устроены юрты?'),
         ('<p>Фотографии помогают познакомиться с предложением, но сами по себе не подтверждают отопление, отдельный санузел, '
          'количество спальных мест или питание. Попросите подтвердить эти условия для конкретного варианта проживания.</p>',
          '<p>Фотографии юрт — на <a href="{b}/ru/pages/47.html">странице о проживании в юртах</a>. Напишите, что для вас '
          'важно — санузел, отопление, число спальных мест или питание, — и мы подтвердим детали на ваши даты.</p>'),
         ('Фотографии помогают познакомиться с предложением, но сами по себе не подтверждают отопление, отдельный санузел, '
          'количество спальных мест или питание. Попросите подтвердить эти условия для конкретного варианта проживания.',
          'Фотографии юрт — на странице о проживании в юртах. Напишите, что для вас важно — санузел, отопление, число '
          'спальных мест или питание, — и мы подтвердим детали на ваши даты.'),
         ('Сообщите менеджеру, хотите ли вы проживание в юрте или другой вариант, и попросите включить согласованные условия '
          'в предложение.',
          'Напишите, что предпочитаете — юрту или гостевой дом, — и мы включим это в план поездки.')])
for _k, _g in G.items():
    assert len(_g['desc']) <= 155, _k
    assert len(_g.get('title', '')) <= 60, _k
# sentences that also appear on the guide index and the other guide pages (cards, related reading)
GUIDE_GLOBAL = [s for k, g in G.items() for s in g['sub'] if s[0].startswith(('Both options', 'В каталоге есть', 'The company offers',
                                                                               'Компания предлагает', 'Send the manager',
                                                                               'Чтобы получить', 'Choose between',
                                                                               'У компании есть'))]


# ---------------------------------------------------------------- helpers
def _key(rel):
    return rel[len('summer/'):] if rel.startswith('summer/') else rel


def _lang(rel):
    return 'en' if _key(rel).startswith('en/') else 'ru'


def _prefix(rel, s):
    return ('/almaty-travel-review' if '/almaty-travel-review/' in s else '') + ('/summer' if rel.startswith('summer/') else '')


def set_meta(s, title=None, desc=None):
    if title:
        s = re.sub(r'<title>[^<]*</title>', lambda m: '<title>%s</title>' % html.escape(title, quote=False), s, count=1)
        for attr in ('property="og:title"', 'name="twitter:title"'):
            s = re.sub(r'(<meta %s content=")[^"]*' % attr, lambda m: m.group(1) + html.escape(title), s)
    if desc:
        for attr in ('name="description"', 'property="og:description"', 'name="twitter:description"'):
            s = re.sub(r'(<meta %s content=")[^"]*' % attr, lambda m: m.group(1) + html.escape(desc), s)
    return s


def set_h1(s, h1):
    def fix(m):
        inner = m.group(2)
        if '<strong>' in inner:
            inner = re.sub(r'(<strong>)[^<]*(</strong>)', lambda x: x.group(1) + html.escape(h1, quote=False) + x.group(2), inner, count=1)
        else:
            inner = html.escape(h1, quote=False)
        return '<h1%s>%s</h1>' % (m.group(1), inner)
    return re.sub(r'<h1([^>]*)>(.*?)</h1>', fix, s, count=1, flags=re.S)


def edit_ld(s, fn):
    def fix(m):
        try:
            data = json.loads(m.group(1))
        except ValueError:
            return m.group(0)
        new = fn(data)
        if new is None:
            return m.group(0)
        compact = ', ' not in m.group(1)[:40]
        return '<script type="application/ld+json">%s</script>' % (
            json.dumps(new, ensure_ascii=False, separators=(',', ':')) if compact else json.dumps(new, ensure_ascii=False))
    return LD.sub(fix, s)


def ld_meta(title, desc, h1):
    def fn(data):
        changed = False
        nodes = data.get('@graph', [data]) if isinstance(data, dict) else []
        for n in nodes:
            t = n.get('@type')
            if t == 'WebPage' and title:
                if n.get('name') != title or n.get('description') != desc:
                    n['name'], n['description'] = title, desc
                    changed = True
            elif t == 'TouristTrip':
                if n.get('description') != desc or (h1 and n.get('name') != h1):
                    n['description'] = desc
                    if h1:
                        n['name'] = h1
                    changed = True
            elif t == 'Article':
                if n.get('description') != desc or (h1 and n.get('headline') != h1):
                    n['description'] = desc
                    if h1:
                        n['headline'] = h1
                    changed = True
        return data if changed else None
    return fn


def org_fn(data):
    if isinstance(data, dict) and data.get('@type') == 'TravelAgency' and data.get('@id') == HOST + '/#organization':
        return ORG if data != ORG else None
    return None


def strip_tags(x):
    return html.unescape(re.sub(r'<[^>]+>', '', x))


def render(block, lang, pre, url, ru_home=False):
    out, faq = [], None
    for h2, body in block:
        if h2 == 'faq':
            faq = body
            out.append('<h2>%s</h2>' % ('Frequently asked questions' if lang == 'en' else 'Частые вопросы'))
            for q, a in body:
                out.append('<h3>%s</h3><p>%s</p>' % (html.escape(q, quote=False), a.replace('{b}', pre)))
        else:
            out.append(('<h2>%s</h2>' % html.escape(h2, quote=False) if h2 else '') + body.replace('{b}', pre))
    sec = '%s<section id="tour-details" class="almaty-seo-block tour-details">%s</section>%s' % (START, ''.join(out), END)
    ld = None
    if faq:
        ld = json.dumps({'@context': 'https://schema.org', '@type': 'FAQPage', '@id': url + '#faq', 'url': url,
                         'mainEntity': [{'@type': 'Question', 'name': q,
                                         'acceptedAnswer': {'@type': 'Answer', 'text': strip_tags(a.replace('{b}', ''))}}
                                        for q, a in faq]}, ensure_ascii=False, separators=(',', ':'))
    return sec, ld


def insert_block(s, sec, anchor):
    if START in s:
        return re.sub(re.escape(START) + r'.*?' + re.escape(END), lambda m: sec, s, count=1, flags=re.S)
    if anchor == 'home':
        m = re.search(r'<section class="almaty-seo-block" data-almaty-seo="choices" id="home-routes">.*?</section>', s, re.S)
        if m:
            return s[:m.end()] + sec + s[m.end():]
        return s
    i = s.rfind('<p class="owner-contact-cta">')
    if i < 0:
        return s
    return s[:i] + sec + s[i:]


def set_faq_ld(s, ld):
    pat = re.compile(r'<script type="application/ld\+json">\{"@context":"https://schema.org","@type":"FAQPage".*?</script>', re.S)
    tag = '<script type="application/ld+json">%s</script>' % ld
    if pat.search(s):
        return pat.sub(lambda m: tag, s, count=1)
    return s.replace('</head>', tag + '\n</head>', 1)


def clean_398(s):
    s = re.sub(r'<source-footnote[^>]*></source-footnote>', '', s)
    s = re.sub(r'\s*<div _ngcontent-ng-[^>]*class="source-inline-chip-container[^"]*">\s*<button[^>]*></button></div>', '', s)
    for _ in range(3):
        s = re.sub(r'<span class="citation-[^"]*">(.*?)</span>', r'\1', s, flags=re.S)
    s = re.sub(r' data-(?:index-in-node|path-to-node)="[^"]*"', '', s)
    s = re.sub(r' id="p-rc_[0-9a-f]+-\d+"', '', s)
    s = s.replace('of ski equipmen</p>', 'of ski equipment</p>')
    return s


def patch(rel, s):
    key, lang = _key(rel), _lang(rel)
    pre = _prefix(rel, s)
    # organisation entity, slogan
    s = edit_ld(s, org_fn)
    s = s.replace(*SLOGAN)
    # guide articles: internal phrases
    if '/guide/' in key:
        s = s.replace(SOURCE_P[lang], '')
        for a, b in (G_EN_COMMON if lang == 'en' else G_RU_COMMON):
            s = s.replace(a, b)
        for a, b in GUIDE_GLOBAL:
            s = s.replace(a, b)
        g = G.get(key)
        if g:
            for a, b in g['sub']:
                s = s.replace(a, b.replace('{b}', pre))
            s = set_meta(s, g.get('title'), g['desc'])
            if g.get('h1'):
                s = set_h1(s, g['h1'])
            s = edit_ld(s, ld_meta(None, g['desc'], g.get('h1')))
    if key.endswith('tours/398/index.html'):
        s = clean_398(s)
    p = P.get(key)
    if p:
        s = set_meta(s, p['title'], p['desc'])
        if p['h1']:
            s = set_h1(s, p['h1'])
        s = edit_ld(s, ld_meta(p['title'], p['desc'], p['h1']))
        if key == 'en/index.html':
            s = re.sub(r'(<p data-almaty-seo="intro">)[^<]*(</p>)', lambda m: m.group(1) + HOME_EN_INTRO + m.group(2), s, count=1)
        if key.endswith('pages/26.html') and 'com-seo-cars' not in s:
            m = re.search(r'(<section id="owner-car-photos"[^>]*><h2>[^<]*</h2>)', s)
            if m:
                s = s[:m.end()] + '<p class="com-seo-cars">%s</p>' % CARS[lang] + s[m.end():]
        if p['block']:
            c = re.search(r'<link rel="canonical" href="([^"]+)"', s)
            url = c.group(1) if c else HOST + '/'
            sec, ld = render(p['block'], lang, pre, url)
            s = insert_block(s, sec, p['anchor'])
            if ld and START in s:
                s = set_faq_ld(s, ld)
    return s


def apply(page_map):
    return {rel: (patch(rel, s) if rel.endswith('.html') else s) for rel, s in page_map.items()}


if __name__ == '__main__':
    repo = sys.argv[1] if len(sys.argv) > 1 else '.'
    n = 0
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in ('.git', 'tools', 'articles')]
        for name in files:
            if not name.endswith('.html'):
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, repo)
            with open(path, encoding='utf-8', newline='') as fh:
                s = fh.read()
            t = patch(rel, s)
            if t != s:
                with open(path, 'w', encoding='utf-8', newline='') as fh:
                    fh.write(t)
                n += 1
    print('changed files:', n)
