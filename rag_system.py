import json
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
import sqlite3

@dataclass
class KnowledgeItem:
    """Элемент знаний предметной области"""
    category: str
    term: str
    definition: str
    examples: Optional[List[str]] = None
    related_terms: Optional[List[str]] = None

class RAGSystem:
    """
    RAG (Retrieval-Augmented Generation) система для работы с контекстными знаниями
    """
    
    def __init__(self):
        self.knowledge_base = self._initialize_knowledge_base()
        
    def _initialize_knowledge_base(self) -> Dict[str, List[KnowledgeItem]]:
        """Инициализация базы знаний"""
        
        knowledge = {
            "metrics": [
                KnowledgeItem(
                    category="metrics",
                    term="CTR (Click-Through Rate)",
                    definition="Отношение количества кликов к количеству показов, выраженное в процентах",
                    examples=["CTR 2.5% означает, что из 100 показов было 2.5 клика"],
                    related_terms=["клики", "показы", "конверсия"]
                ),
                KnowledgeItem(
                    category="metrics", 
                    term="CPC (Cost Per Click)",
                    definition="Стоимость за клик - средняя стоимость одного клика по рекламе",
                    examples=["CPC 50 рублей означает, что каждый клик стоит 50 рублей"],
                    related_terms=["стоимость", "клики", "бюджет"]
                ),
                KnowledgeItem(
                    category="metrics",
                    term="CPM (Cost Per Mille)", 
                    definition="Стоимость за 1000 показов рекламы",
                    examples=["CPM 1000 рублей означает, что 1000 показов стоят 1000 рублей"],
                    related_terms=["показы", "стоимость", "охват"]
                ),
                KnowledgeItem(
                    category="metrics",
                    term="Конверсия",
                    definition="Отношение целевых действий к общему количеству визитов",
                    examples=["Конверсия 5% означает, что из 100 визитов 5 привели к цели"],
                    related_terms=["визиты", "цели", "эффективность"]
                ),
                KnowledgeItem(
                    category="metrics",
                    term="ROI (Return on Investment)",
                    definition="Возврат инвестиций - отношение прибыли к затратам",
                    examples=["ROI 300% означает, что на каждый рубль затрат получено 3 рубля прибыли"],
                    related_terms=["прибыль", "затраты", "эффективность"]
                ),
                KnowledgeItem(
                    category="metrics",
                    term="AOV (Average Order Value)",
                    definition="Средний чек. Средняя стоимость заказа или покупки",
                    examples=["AOV рассчитывается как выручка / количество заказов"],
                    related_terms=["средний чек", "заказы", "выручка", "покупки"]
                ),
                KnowledgeItem(
                    category="metrics",
                    term="CAC (Customer Acquisition Cost)",
                    definition="Средняя стоимость привлечения уникального клиента",
                    examples=["CAC рассчитывается как расходы на канал трафика / привлеченные клиенты"],
                    related_terms=["привлечение клиентов", "стоимость", "трафик", "клиенты"]
                ),
                KnowledgeItem(
                    category="metrics",
                    term="CPI (Cost per Impression)",
                    definition="Стоимость показа рекламы, в том числе повторно одному и тому же человеку",
                    examples=["CPI показывает стоимость одного показа рекламы"],
                    related_terms=["показы", "стоимость", "реклама", "показатели"]
                ),
                KnowledgeItem(
                    category="metrics",
                    term="CPA (Cost Per Action)",
                    definition="Стоимость за действие - стоимость привлечения клиента, совершившего целевое действие",
                    examples=["CPA рассчитывается как расходы на рекламу / количество целевых действий"],
                    related_terms=["действия", "стоимость", "целевые действия", "привлечение"]
                ),
                KnowledgeItem(
                    category="metrics",
                    term="BR (Bounce Rate)",
                    definition="Показатель отказов: процент пользователей, которые покинули сайт, просмотрев только страницу входа",
                    examples=["BR 50% означает, что половина посетителей ушли с первой страницы"],
                    related_terms=["отказы", "посетители", "сайт", "удержание"]
                ),
                KnowledgeItem(
                    category="metrics",
                    term="Average page view duration",
                    definition="Время, которое пользователь в среднем проводит на одной странице сайта",
                    examples=["Среднее время на странице показывает вовлеченность пользователей"],
                    related_terms=["время на сайте", "страницы", "вовлеченность", "пользователи"]
                )
            ],
            
            "platforms": [
                KnowledgeItem(
                    category="platforms",
                    term="Яндекс.Директ",
                    definition="Контекстная реклама от Яндекса с показом в поиске и на сайтах-партнерах",
                    examples=["Реклама показывается при поиске 'открыть счет в банке'"],
                    related_terms=["контекстная реклама", "поиск", "баннеры"]
                ),
                KnowledgeItem(
                    category="platforms", 
                    term="VK Реклама",
                    definition="Реклама в социальной сети ВКонтакте с таргетингом по интересам",
                    examples=["Реклама показывается пользователям с интересом к бизнесу"],
                    related_terms=["социальные сети", "таргетинг", "интересы"]
                ),
                KnowledgeItem(
                    category="platforms",
                    term="Telegram Ads",
                    definition="Реклама в мессенджере Telegram с показом в каналах и ботах",
                    examples=["Реклама в каналах о бизнесе и предпринимательстве"],
                    related_terms=["мессенджер", "каналы", "боти"]
                ),
                KnowledgeItem(
                    category="platforms",
                    term="MyTarget",
                    definition="Рекламная платформа от VK с показом на сайтах-партнерах",
                    examples=["Реклама на сайтах о финансах и бизнесе"],
                    related_terms=["рекламная сеть", "сайты-партнеры", "таргетинг"]
                )
            ],
            
            "analysis": [
                KnowledgeItem(
                    category="analysis",
                    term="Анализ эффективности",
                    definition="Оценка результатов рекламных кампаний по ключевым метрикам",
                    examples=["Сравнение CTR и CPC разных кампаний"],
                    related_terms=["метрики", "сравнение", "результаты"]
                ),
                KnowledgeItem(
                    category="analysis",
                    term="Трендовый анализ", 
                    definition="Анализ изменений показателей во времени",
                    examples=["Как менялся CTR кампании по дням"],
                    related_terms=["время", "динамика", "изменения"]
                ),
                KnowledgeItem(
                    category="analysis",
                    term="Сегментация аудитории",
                    definition="Разделение аудитории на группы по характеристикам",
                    examples=["Анализ по возрастным группам или регионам"],
                    related_terms=["аудитория", "группы", "характеристики"]
                ),
                KnowledgeItem(
                    category="analysis", 
                    term="A/B тестирование",
                    definition="Сравнение двух вариантов рекламы для выбора лучшего",
                    examples=["Тестирование разных заголовков или изображений"],
                    related_terms=["сравнение", "тестирование", "оптимизация"]
                )
            ],
            
            "optimization": [
                KnowledgeItem(
                    category="optimization",
                    term="Оптимизация бюджета",
                    definition="Перераспределение бюджета между кампаниями для максимизации ROI",
                    examples=["Увеличение бюджета на кампании с высоким CTR"],
                    related_terms=["бюджет", "ROI", "эффективность"]
                ),
                KnowledgeItem(
                    category="optimization",
                    term="Оптимизация креативов",
                    definition="Улучшение рекламных материалов для повышения CTR",
                    examples=["Изменение заголовков, изображений, текстов"],
                    related_terms=["креативы", "CTR", "материалы"]
                ),
                KnowledgeItem(
                    category="optimization",
                    term="Таргетинг",
                    definition="Настройка показа рекламы целевой аудитории",
                    examples=["Показ рекламы предпринимателям 25-45 лет"],
                    related_terms=["аудитория", "настройка", "цели"]
                ),
                KnowledgeItem(
                    category="optimization",
                    term="Географический таргетинг",
                    definition="Показ рекламы в определенных регионах",
                    examples=["Реклама только в Москве и Санкт-Петербурге"],
                    related_terms=["регионы", "география", "локация"]
                )
            ],
            
            "business_terms": [
                KnowledgeItem(
                    category="business_terms",
                    term="ДМиК",
                    definition="Департамент маркетинга и коммуникаций. Предлагает различные услуги для команд, включая исследование потребителей и конкурентов, подготовку продуктовых гипотез и их тестирование, проведение рекламных кампаний, поддержку при участии в мероприятиях, продвижение на собственных медиаресурсах и брендинг",
                    examples=["ДМиК помогает командам достигать роста пользователей продуктов и сервисов, увеличивать конверсию из рекламных каналов, развивать бренды и эффективно взаимодействовать с подразделениями"],
                    related_terms=["маркетинг", "коммуникации", "рекламные кампании", "брендинг", "исследования", "ДМИК", "дмик"]
                ),
                KnowledgeItem(
                    category="business_terms",
                    term="ДМИК",
                    definition="Департамент маркетинга и коммуникаций. Предлагает различные услуги для команд, включая исследование потребителей и конкурентов, подготовку продуктовых гипотез и их тестирование, проведение рекламных кампаний, поддержку при участии в мероприятиях, продвижение на собственных медиаресурсах и брендинг",
                    examples=["ДМИК помогает командам достигать роста пользователей продуктов и сервисов, увеличивать конверсию из рекламных каналов, развивать бренды и эффективно взаимодействовать с подразделениями"],
                    related_terms=["маркетинг", "коммуникации", "рекламные кампании", "брендинг", "исследования", "ДМиК", "дмик"]
                ),
                KnowledgeItem(
                    category="business_terms",
                    term="РКО",
                    definition="Расчетно-кассовое обслуживание - банковские услуги по ведению расчетных счетов юридических лиц",
                    examples=["РКО включает открытие счета, проведение платежей, выдачу выписок"],
                    related_terms=["расчетный счет", "платежи", "банковские услуги", "юридические лица"]
                ),
                KnowledgeItem(
                    category="business_terms",
                    term="РБИДОС",
                    definition="Расчетно-кассовое обслуживание для индивидуальных предпринимателей и физических лиц",
                    examples=["РБИДОС позволяет ИП и физлицам вести расчеты через банк"],
                    related_terms=["ИП", "физлица", "расчеты", "банковские услуги"]
                ),
                KnowledgeItem(
                    category="business_terms",
                    term="Бизнес-карты",
                    definition="Банковские карты для юридических лиц и ИП, предназначенные для оплаты корпоративных расходов",
                    examples=["Бизнес-карты позволяют контролировать расходы сотрудников на командировки"],
                    related_terms=["корпоративные расходы", "контроль", "командировки", "ИП"]
                ),
                KnowledgeItem(
                    category="business_terms",
                    term="Бизнес-кредиты",
                    definition="Кредитные продукты для юридических лиц и ИП, предназначенные для развития бизнеса",
                    examples=["Бизнес-кредиты могут быть целевыми на закупку оборудования или оборотные"],
                    related_terms=["кредитование", "развитие бизнеса", "оборудование", "оборотные средства"]
                ),
                KnowledgeItem(
                    category="business_terms",
                    term="ФРК4",
                    definition="ФРК4 - рекламная кампания для продвижения банковских продуктов",
                    examples=["ФРК4 кампания направлена на привлечение клиентов для банковских услуг"],
                    related_terms=["рекламная кампания", "банковские продукты", "привлечение клиентов"]
                ),
                KnowledgeItem(
                    category="business_terms",
                    term="ФРК",
                    definition="ФРК - семейство рекламных кампаний для различных банковских продуктов",
                    examples=["ФРК кампании включают ФРК1, ФРК2, ФРК3, ФРК4 и другие"],
                    related_terms=["рекламные кампании", "банковские продукты", "семейство кампаний"]
                ),
                KnowledgeItem(
                    category="business_terms",
                    term="Маркетинг",
                    definition="Комплекс мероприятий по продвижению продуктов и услуг, включающий исследование рынка, рекламу, PR и продажи",
                    examples=["Маркетинг включает анализ конкурентов, позиционирование продукта, рекламные кампании"],
                    related_terms=["продвижение", "реклама", "исследования", "PR", "продажи"]
                ),
                KnowledgeItem(
                    category="business_terms",
                    term="Коммуникации",
                    definition="Совокупность каналов и методов взаимодействия с целевой аудиторией",
                    examples=["Коммуникации включают рекламу, PR, социальные сети, email-рассылки"],
                    related_terms=["каналы", "взаимодействие", "аудитория", "реклама", "PR"]
                ),
                KnowledgeItem(
                    category="business_terms",
                    term="Брендинг",
                    definition="Создание и развитие уникального образа бренда в сознании потребителей",
                    examples=["Брендинг включает разработку логотипа, фирменного стиля, позиционирования"],
                    related_terms=["бренд", "образ", "позиционирование", "логотип", "стиль"]
                ),
                KnowledgeItem(
                    category="business_terms",
                    term="Исследования",
                    definition="Систематический сбор и анализ данных для принятия маркетинговых решений",
                    examples=["Исследования включают анализ конкурентов, изучение потребителей, тестирование гипотез"],
                    related_terms=["анализ", "данные", "решения", "конкуренты", "потребители"]
                ),
                KnowledgeItem(
                    category="business_terms",
                    term="Рекламные кампании",
                    definition="Комплекс мероприятий по продвижению продукта или услуги через различные каналы рекламы",
                    examples=["Рекламные кампании включают планирование, создание креативов, размещение, анализ результатов"],
                    related_terms=["реклама", "продвижение", "креативы", "размещение", "анализ"]
                ),
                KnowledgeItem(
                    category="business_terms",
                    term="Мероприятия",
                    definition="Организованные события для продвижения бренда или продукта",
                    examples=["Мероприятия включают конференции, выставки, презентации, вебинары"],
                    related_terms=["события", "продвижение", "конференции", "выставки", "презентации"]
                ),
                KnowledgeItem(
                    category="business_terms",
                    term="Медиаресурсы",
                    definition="Собственные каналы коммуникации компании для продвижения контента",
                    examples=["Медиаресурсы включают корпоративный сайт, блог, социальные сети компании"],
                    related_terms=["каналы", "коммуникация", "контент", "сайт", "социальные сети"]
                ),
                KnowledgeItem(
                    category="business_terms",
                    term="Продуктовые гипотезы",
                    definition="Предположения о том, как улучшить продукт или создать новый продукт",
                    examples=["Продуктовые гипотезы тестируются через A/B тесты, опросы пользователей, аналитику"],
                    related_terms=["гипотезы", "продукт", "тестирование", "A/B тесты", "аналитика"]
                ),
                KnowledgeItem(
                    category="business_terms",
                    term="Конверсия",
                    definition="Отношение целевых действий к общему количеству посетителей",
                    examples=["Конверсия 5% означает, что из 100 посетителей 5 совершили целевое действие"],
                    related_terms=["эффективность", "цели", "действия", "посетители", "результаты"]
                ),
                KnowledgeItem(
                    category="business_terms",
                    term="Рост пользователей",
                    definition="Увеличение количества активных пользователей продукта или сервиса",
                    examples=["Рост пользователей измеряется через количество регистраций, активность, удержание"],
                    related_terms=["пользователи", "активность", "регистрации", "удержание", "развитие"]
                ),
                KnowledgeItem(
                    category="business_terms",
                    term="Команды",
                    definition="Рабочие группы, отвечающие за разработку и продвижение продуктов",
                    examples=["Команды включают разработчиков, дизайнеров, маркетологов, аналитиков"],
                    related_terms=["группы", "разработка", "продвижение", "продукты", "сотрудники"]
                ),
                KnowledgeItem(
                    category="business_terms",
                    term="Подразделения",
                    definition="Структурные единицы организации, выполняющие определенные функции",
                    examples=["Подразделения включают отделы маркетинга, разработки, продаж, поддержки"],
                    related_terms=["структура", "организация", "функции", "отделы", "роли"]
                ),
                KnowledgeItem(
                    category="business_terms",
                    term="Потребители",
                    definition="Люди, которые используют или могут использовать продукты и услуги компании",
                    examples=["Потребители изучаются через опросы, интервью, анализ поведения"],
                    related_terms=["клиенты", "пользователи", "аудитория", "исследования", "поведение"]
                ),
                KnowledgeItem(
                    category="business_terms",
                    term="Конкуренты",
                    definition="Компании, предлагающие аналогичные продукты или услуги",
                    examples=["Конкуренты анализируются для понимания их сильных и слабых сторон"],
                    related_terms=["анализ", "рынок", "продукты", "услуги", "стратегия"]
                )
            ],
            
            "campaigns": [
                KnowledgeItem(
                    category="campaigns",
                    term="ФРК4",
                    definition="Рекламная кампания ФРК4 для продвижения банковских продуктов",
                    examples=["ФРК4 кампания направлена на привлечение клиентов для банковских услуг"],
                    related_terms=["рекламная кампания", "банковские продукты", "привлечение клиентов", "ФРК"]
                ),
                KnowledgeItem(
                    category="campaigns",
                    term="ФРК",
                    definition="Семейство рекламных кампаний ФРК для различных банковских продуктов",
                    examples=["ФРК кампании включают ФРК1, ФРК2, ФРК3, ФРК4 и другие"],
                    related_terms=["рекламные кампании", "банковские продукты", "семейство кампаний"]
                ),
                KnowledgeItem(
                    category="campaigns",
                    term="РКО кампании",
                    definition="Рекламные кампании для продвижения расчетно-кассового обслуживания",
                    examples=["РКО кампании направлены на привлечение юридических лиц для банковского обслуживания"],
                    related_terms=["РКО", "рекламные кампании", "юридические лица", "банковские услуги"]
                ),
                KnowledgeItem(
                    category="campaigns",
                    term="РБИДОС кампании",
                    definition="Рекламные кампании для продвижения расчетно-кассового обслуживания для ИП и физлиц",
                    examples=["РБИДОС кампании направлены на привлечение ИП и физических лиц"],
                    related_terms=["РБИДОС", "рекламные кампании", "ИП", "физлица", "банковские услуги"]
                ),
                KnowledgeItem(
                    category="campaigns",
                    term="Бизнес-карты кампании",
                    definition="Рекламные кампании для продвижения корпоративных банковских карт",
                    examples=["Бизнес-карты кампании направлены на привлечение юридических лиц и ИП"],
                    related_terms=["Бизнес-карты", "рекламные кампании", "корпоративные карты", "ИП"]
                ),
                KnowledgeItem(
                    category="campaigns",
                    term="Бизнес-кредиты кампании",
                    definition="Рекламные кампании для продвижения кредитных продуктов для бизнеса",
                    examples=["Бизнес-кредиты кампании направлены на привлечение юридических лиц и ИП"],
                    related_terms=["Бизнес-кредиты", "рекламные кампании", "кредитование", "бизнес"]
                )
            ],
            
            "bank_terms": [
                KnowledgeItem(
                    category="bank_terms",
                    term="КИБ",
                    definition="Корпоративно-инвестиционный бизнес. Подразделение банка, которое занимается различными задачами, связанными с корпоративными клиентами и инвестиционными услугами",
                    examples=["КИБ обслуживает крупные корпорации и предоставляет инвестиционные услуги"],
                    related_terms=["корпоративный бизнес", "инвестиции", "подразделение", "банк"]
                ),
                KnowledgeItem(
                    category="bank_terms",
                    term="МКИБ",
                    definition="Трайб «Маркетинг КИБ». Подразделение, отвечающее за маркетинг корпоративно-инвестиционного бизнеса",
                    examples=["МКИБ разрабатывает маркетинговые стратегии для корпоративных клиентов"],
                    related_terms=["маркетинг", "КИБ", "трайб", "корпоративные клиенты"]
                ),
                KnowledgeItem(
                    category="bank_terms",
                    term="ММБ",
                    definition="Трайб «Малый и Микро Бизнес». Подразделение, работающее с малым и микробизнесом",
                    examples=["ММБ предоставляет услуги для ИП и небольших компаний"],
                    related_terms=["малый бизнес", "микробизнес", "ИП", "трайб"]
                ),
                KnowledgeItem(
                    category="bank_terms",
                    term="СББОЛ",
                    definition="Сокращенное название «Сбербанк Бизнес Онлайн», системы дистанционного обслуживания юридических лиц и ИП",
                    examples=["СББОЛ позволяет управлять счетами и проводить операции через интернет"],
                    related_terms=["Сбербанк", "бизнес онлайн", "дистанционное обслуживание", "юридические лица", "ИП"]
                ),
                KnowledgeItem(
                    category="bank_terms",
                    term="ТАКБ",
                    definition="Транзакционно-активная база. База транзакций клиентов по банкам",
                    examples=["ТАКБ содержит данные о всех операциях клиентов банка"],
                    related_terms=["транзакции", "база данных", "клиенты", "операции"]
                ),
                KnowledgeItem(
                    category="bank_terms",
                    term="ЧОД",
                    definition="Чистый операционный доход. Финансовый показатель, отражающий доходы за вычетом операционных расходов",
                    examples=["ЧОД рассчитывается как выручка минус операционные расходы"],
                    related_terms=["доход", "финансы", "операционные расходы", "прибыль"]
                ),
                KnowledgeItem(
                    category="bank_terms",
                    term="МАРК",
                    definition="Платформа человекоцентричного маркетинга. Единая платформа управления процессами и стратегическими задачами маркетинга",
                    examples=["МАРК помогает управлять маркетинговыми процессами и стратегиями"],
                    related_terms=["платформа", "маркетинг", "управление", "стратегии"]
                ),
                KnowledgeItem(
                    category="bank_terms",
                    term="ОТР",
                    definition="Продукт «Отраслевые решения» для розничной торговли. Специализированные банковские продукты для торговых компаний",
                    examples=["ОТР включает специальные условия для розничных торговых сетей"],
                    related_terms=["отраслевые решения", "розничная торговля", "торговые сети", "специализированные продукты"]
                )
            ]
        }
        
        return knowledge
    
    def search_knowledge(self, query: str) -> List[KnowledgeItem]:
        """
        Поиск релевантных знаний по запросу с улучшенным алгоритмом
        """
        query_lower = query.lower().strip()
        relevant_items = []
        
        # Разбиваем запрос на слова для более точного поиска
        query_words = query_lower.split()
        
        for category, items in self.knowledge_base.items():
            for item in items:
                score = 0
                
                # Проверяем точное совпадение в термине (высший приоритет)
                if query_lower == item.term.lower():
                    score += 100
                
                # Проверяем частичное совпадение в термине
                elif query_lower in item.term.lower():
                    score += 80
                
                # Проверяем совпадение отдельных слов в термине
                elif any(word in item.term.lower() for word in query_words):
                    score += 60
                
                # Проверяем совпадение в определении
                if query_lower in item.definition.lower():
                    score += 40
                elif any(word in item.definition.lower() for word in query_words):
                    score += 30
                
                # Проверяем связанные термины
                if item.related_terms:
                    for term in item.related_terms:
                        if query_lower in term.lower():
                            score += 50
                            break
                        elif any(word in term.lower() for word in query_words):
                            score += 25
                
                # Проверяем примеры
                if item.examples:
                    for example in item.examples:
                        if query_lower in example.lower():
                            score += 30
                            break
                        elif any(word in example.lower() for word in query_words):
                            score += 15
                
                # Добавляем элемент, если набрал достаточно баллов
                if score > 0:
                    relevant_items.append((item, score))
        
        # Сортируем по релевантности и убираем дубликаты
        relevant_items.sort(key=lambda x: x[1], reverse=True)
        seen_terms = set()
        unique_items = []
        
        for item, score in relevant_items:
            if item.term not in seen_terms:
                unique_items.append(item)
                seen_terms.add(item.term)
        
        return unique_items
    
    def get_context_for_question(self, question: str) -> str:
        """
        Получение контекста для ответа на вопрос
        """
        relevant_items = self.search_knowledge(question)
        
        if not relevant_items:
            return ""
        
        context = "## Контекстные знания:\n\n"
        
        for item in relevant_items:
            context += f"### {item.term}\n"
            context += f"{item.definition}\n\n"
            
            if item.examples:
                context += "**Примеры:**\n"
                for example in item.examples:
                    context += f"- {example}\n"
                context += "\n"
            
            if item.related_terms:
                context += f"**Связанные термины:** {', '.join(item.related_terms)}\n\n"
        
        return context
    
    def get_recommendations(self, analysis_results: Dict) -> List[str]:
        """
        Генерация рекомендаций на основе анализа
        """
        recommendations = []
        
        # Анализ CTR
        if 'avg_ctr' in analysis_results:
            ctr = analysis_results['avg_ctr']
            if ctr < 0.5:
                recommendations.append("Низкий CTR требует оптимизации креативов и таргетинга")
            elif ctr > 3:
                recommendations.append("Высокий CTR - можно увеличить бюджет на эти кампании")
        
        # Анализ CPC
        if 'avg_cpc' in analysis_results:
            cpc = analysis_results['avg_cpc']
            if cpc > 100:
                recommendations.append("Высокий CPC - рассмотрите оптимизацию ставок")
        
        # Анализ по площадкам
        if 'platforms' in analysis_results:
            for platform in analysis_results['platforms']:
                if platform['ctr'] > 3:
                    recommendations.append(f"Увеличить бюджет на {platform['platform']} - высокий CTR {platform['ctr']}%")
                elif platform['ctr'] < 0.3:
                    recommendations.append(f"Пересмотреть креативы на {platform['platform']} - низкий CTR {platform['ctr']}%")
        
        return recommendations
    
    def enhance_report(self, report: str, question: str) -> str:
        """
        Улучшение отчета с помощью контекстных знаний
        """
        context = self.get_context_for_question(question)
        
        if context:
            enhanced_report = context + "\n" + report
            return enhanced_report
        
        return report

# Пример использования
if __name__ == "__main__":
    rag = RAGSystem()
    
    # Тестирование поиска знаний
    test_queries = [
        "Что такое CTR?",
        "Как работает Яндекс.Директ?",
        "Что такое оптимизация бюджета?",
        "Как анализировать эффективность?"
    ]
    
    for query in test_queries:
        print(f"\nЗапрос: {query}")
        items = rag.search_knowledge(query)
        if items:
            print(f"Найдено {len(items)} релевантных элементов:")
            for item in items:
                print(f"- {item.term}: {item.definition}")
        else:
            print("Релевантные знания не найдены") 