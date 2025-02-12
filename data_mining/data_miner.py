import mwclient
import mwparserfromhell
import re

# поиск страниц Википедии о летних Олимпийских играх 2028 года 
 
# Задаем категорию и англоязычную версию Википедии для поиска 
CATEGORY_TITLE = "Category:2028 Summer Olympics" 
WIKI_SITE = "en.wikipedia.org" 
 
# Соберем заголовки всех статей 
def titles_from_category( 
    category: mwclient.listing.Category, # Задаем типизированный параметр категории статей 
    max_depth: int # Определяем глубину вложения статей 
) -> set[str]: 
    """Возвращает набор заголовков страниц в данной категории Википедии и ее подкатегориях.""" 
    titles = set() # Используем множество для хранения заголовков статей 
    for cm in category.members(): # Перебираем вложенные объекты категории 
        if type(cm) == mwclient.page.Page: # Если объект является страницей 
            titles.add(cm.name) # в хранилище заголовков добавляем имя страницы 
        elif isinstance(cm, mwclient.listing.Category) and max_depth > 0: # Если объект является категорией и глубина вложения не достигла максимальной 
            deeper_titles = titles_from_category(cm, max_depth=max_depth - 1) # вызываем рекурсивно функцию для подкатегории 
            titles.update(deeper_titles) # добавление в множество элементов из другого множества 
    return titles 
 
# Инициализация объекта MediaWiki 
# WIKI_SITE ссылается на англоязычную часть Википедии 
site = mwclient.Site(WIKI_SITE) 
 
# Загрузка раздела заданной категории 
category_page = site.pages[CATEGORY_TITLE] 
# Получение множества всех заголовков категории с вложенностью на один уровень 
titles = titles_from_category(category_page, max_depth=1) 
 
 
print(f"Создано {len(titles)} заголовков статей в категории {CATEGORY_TITLE}.")

# Задаем секции, которые будут отброшены при парсинге статей 
SECTIONS_TO_IGNORE = [ 
    "See also", 
    "References", 
    "External links", 
    "Further reading", 
    "Footnotes", 
    "Bibliography", 
    "Sources", 
    "Citations", 
    "Literature", 
    "Footnotes", 
    "Notes and references", 
    "Photo gallery", 
    "Works cited", 
    "Photos", 
    "Gallery", 
    "Notes", 
    "References and sources", 
    "References and notes", 
] 


# Функция возвращает список всех вложенных секций для заданной секции страницы Википедии 
 
def all_subsections_from_section( 
    section: mwparserfromhell.wikicode.Wikicode, # текущая секция 
    parent_titles: list[str], # Заголовки родителя 
    sections_to_ignore: set[str], # Секции, которые необходимо проигнорировать 
) -> list[tuple[list[str], str]]: 
    """ 
    Из раздела Википедии возвращает список всех вложенных секций. 
    Каждый подраздел представляет собой кортеж, где: 
      - первый элемент представляет собой список родительских секций, начиная с заголовка страницы 
      - второй элемент представляет собой текст секции 
    """ 
 
    # Извлекаем заголовки текущей секции 
    headings = [str(h) for h in section.filter_headings()] 
    title = headings[0] 
    # Заголовки Википедии имеют вид: "== Heading ==" 
 
    if title.strip("=" + " ") in sections_to_ignore: 
        # Если заголовок секции в списке для игнора, то пропускаем его 
        return [] 
 
    # Объединим заголовки и подзаголовки, чтобы сохранить контекст для chatGPT 
    titles = parent_titles + [title] 
 
    # Преобразуем wikicode секции в строку 
    full_text = str(section) 
 
    # Выделяем текст секции без заголовка 
    section_text = full_text.split(title)[1] 
    if len(headings) == 1: 
        # Если один заголовок, то формируем результирующий список 
        return [(titles, section_text)] 
    else: 
        first_subtitle = headings[1] 
        section_text = section_text.split(first_subtitle)[0] 
        # Формируем результирующий список из текста до первого подзаголовка 
        results = [(titles, section_text)] 
        for subsection in section.get_sections(levels=[len(titles) + 1]): 
            results.extend( 
                # Вызываем функцию получения вложенных секций для заданной секции 
                all_subsections_from_section(subsection, titles, sections_to_ignore) 
                )  # Объединяемрезультирующие списки данной функции и вызываемой 
        return results 
 
# Функция возвращает список всех секций страницы, за исключением тех, которые отбрасываем 
def all_subsections_from_title( 
    title: str, # Заголовок статьи Википедии, которую парсим 
    sections_to_ignore: set[str] = SECTIONS_TO_IGNORE, # Секции, которые игнорируем 
    site_name: str = WIKI_SITE, # Ссылка на сайт википедии 
) -> list[tuple[list[str], str]]: 
    """ 
    Из заголовка страницы Википедии возвращает список всех вложенных секций. 
    Каждый подраздел представляет собой кортеж, где: 
      - первый элемент представляет собой список родительских секций, начиная с заголовка страницы 
      - второй элемент представляет собой текст секции 
    """ 
 
    # Инициализация объекта MediaWiki 
    # WIKI_SITE ссылается на англоязычную часть Википедии 
    site = mwclient.Site(site_name) 
 
    # Запрашиваем страницу по заголовку 
    page = site.pages[title] 
 
    # Получаем текстовое представление страницы 
    text = page.text() 
 
    # Удобный парсер для MediaWiki 
    parsed_text = mwparserfromhell.parse(text) 
    # Извлекаем заголовки 
    headings = [str(h) for h in parsed_text.filter_headings()] 
    if headings: # Если заголовки найдены 
        # В качестве резюме берем текст до первого заголовка 
        summary_text = str(parsed_text).split(headings[0])[0] 
    else: 
        # Если нет заголовков, то весь текст считаем резюме 
        summary_text = str(parsed_text) 
    results = [([title], summary_text)] # Добавляем резюме в результирующий список 
    for subsection in parsed_text.get_sections(levels=[2]): # Извлекаем секции 2-го уровня 
        results.extend( 
            # Вызываем функцию получения вложенных секций для заданной секции 
            all_subsections_from_section(subsection, [title], sections_to_ignore) 
        ) # Объединяем результирующие списки данной функции и вызываемой 
    return results

# Разбивка статей на секции 
# придется немного подождать, так как на парсинг 100 статей требуется около минуты 
wikipedia_sections = [] 
for title in titles: 
    wikipedia_sections.extend(all_subsections_from_title(title)) 
print(f"Найдено {len(wikipedia_sections)} секций на {len(titles)} страницах")

# Очистка текста секции от ссылок <ref>xyz</ref>, начальных и конечных пробелов 
def clean_section(section: tuple[list[str], str]) -> tuple[list[str], str]: 
    titles, text = section 
    # Удаляем ссылки 
    text = re.sub(r"<ref.*?</ref>", "", text) 
    # Удаляем пробелы вначале и конце 
    text = text.strip() 
    return (titles, text) 
 
# Применим функцию очистки ко всем секциям с помощью генератора списков 
wikipedia_sections = [clean_section(ws) for ws in wikipedia_sections] 
 
# Отфильтруем короткие и пустые секции 
def keep_section(section: tuple[list[str], str]) -> bool: 
    """Возвращает значение True, если раздел должен быть сохранен, в противном случае значение False.""" 
    titles, text = section 
    # Фильтруем по произвольной длине, можно выбрать и другое значение 
    if len(text) < 16: 
        return False 
    else: 
        return True 
 
 
original_num_sections = len(wikipedia_sections) 
wikipedia_sections = [ws for ws in wikipedia_sections if keep_section(ws)] 
print(f"Отфильтровано {original_num_sections-len(wikipedia_sections)} секций, осталось {len(wikipedia_sections)} секций.")