import numpy as np
import faiss
import pickle
import os
from sentence_transformers import SentenceTransformer
from typing import List, Dict

class SimpleVectorRAG:
    def __init__(self):
        """Простая векторная RAG система"""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Быстрая модель
        self.index = None
        self.knowledge_items = []
        self.index_file = "simple_rag_index.faiss"
        
        # Загружаем знания
        self._load_knowledge()
        self._build_index()
    
    def _load_knowledge(self):
        """Загружает базу знаний"""
        self.knowledge_items = [
            # Банковские термины
            {"term": "КИБ", "definition": "Корпоративно-инвестиционный бизнес. Подразделение банка, которое занимается различными задачами, связанными с корпоративным и инвестиционным бизнесом"},
            {"term": "МКИБ", "definition": "Трайб «Маркетинг КИБ». Подразделение за маркетинг корпоративно-инвестиционного бизнеса"},
            {"term": "ММБ", "definition": "Трайб «Малый и Микро Бизнес». Подразделение для малого и микробизнеса"},
            {"term": "СББОЛ", "definition": "Сокращенное название «Сбербанк Бизнес Онлайн», системы дистанционного обслуживания юридических лиц и индивидуальных предпринимателей"},
            {"term": "ТАКБ", "definition": "Транзакционно-активная база. База транзакций клиентов по банкам"},
            {"term": "ЧОД", "definition": "Чистый операционный доход. Финансовый показатель доходов за вычетом операционных расходов"},
            {"term": "МАРК", "definition": "Платформа человекоцентричного маркетинга. Единая платформа управления процессами и стратегическими задачами подразделений маркетинга"},
            {"term": "ОТР", "definition": "Продукт «Отраслевые решения» для розничной торговли. Специализированные банковские продукты"},
            {"term": "РКО", "definition": "Расчетно-кассовое обслуживание. Основной корпоративный продукт, продвигаемый маркетингом КИБ. Позволяет совершать безналичные расчеты между организациями и является основой взаимодействия клиента с банком"},
            {"term": "ФРК", "definition": "Федеральная рекламная кампания. Семейство рекламных кампаний для банковских продуктов"},
            
            # Метрики и показатели
            {"term": "AOV", "definition": "Average Order Value - средний чек. Формула расчета: Выручка / Заказы или Выручка / Продажи"},
            {"term": "CAC", "definition": "Customer Acquisition Cost - средняя стоимость привлечения уникального клиента. Формула расчета: Расходы на канал трафика / Привлеченные клиенты"},
            {"term": "CPI", "definition": "Cost per Impression - стоимость показа рекламы, в том числе повторно одному и тому же человеку"},
            {"term": "CPA", "definition": "Cost Per Action - средний расход на получение одной конверсии, или средняя цена, или стоимость целевого действия. Формула расчета: Расход / Конверсии"},
            {"term": "BR", "definition": "Bounce Rate - показатель отказов: процент пользователей, которые покинули сайт, просмотрев только страницу входа"},
            {"term": "CTR", "definition": "Click-Through Rate - отношение кликов к показам в процентах"},
            {"term": "CPC", "definition": "Cost Per Click - средняя стоимость одного клика. Формула расчета: Расход / Клики"},
            {"term": "CPM", "definition": "Cost Per Mille - средняя стоимость за 1000 показов баннера, объявления или другого коммерческого блока. Формула расчета: (Расход / Показы) × 1000"},
            {"term": "ROI", "definition": "Return on Investment - возврат инвестиций, отношение прибыли к затратам"},
            {"term": "CPL", "definition": "Cost Per Lead - средняя цена или стоимость полученных контактов потенциального покупателя. Формула расчета: Расход / Лиды"},
            {"term": "CPO", "definition": "Cost Per Order - средняя стоимость заказа. Формула расчета: Расход / Заказы"},
            {"term": "CPS", "definition": "Cost Per Sale - средняя стоимость продажи. Формула расчета: Расход / Продажи"},
            {"term": "CPV", "definition": "Cost Per View - средняя стоимость просмотра видеорекламы. Формула расчета: Расход / Число просмотров рекламного ролика"},
            {"term": "CR", "definition": "Conversion Rate - соотношение количества целевых действий с общим количеством посещений сайта или приложения. Формула расчета: (Количество целевых действий / Общее количество посещений) * 100%"},
            {"term": "ДРР", "definition": "Доля рекламных расходов - финансовая метрика, показывающая отношение затрат на рекламу к полученному доходу от этой рекламы. Формула расчета: (Расходы на рекламу / Доход от рекламы) * 100%"},
            {"term": "Average page view duration", "definition": "Время, которое пользователь в среднем проводит на одной странице сайта"},
            
            # Бизнес-термины
            {"term": "ДМИК", "definition": "Департамент маркетинга и коммуникаций. Предлагает услуги для команд включая исследования, рекламные кампании, брендинг"},
            {"term": "ФРК4", "definition": "Федеральная рекламная кампания 4. Рекламная кампания для продвижения банковских продуктов"},
            {"term": "Маркетинг", "definition": "Комплекс мероприятий по продвижению продуктов и услуг включающий исследование рынка, позиционирование, рекламу"},
            {"term": "Коммуникации", "definition": "Совокупность каналов и методов взаимодействия с целевой аудиторией"},
            {"term": "Брендинг", "definition": "Создание и развитие уникального образа бренда в сознании потребителей"},
            {"term": "УТП", "definition": "Уникальное торговое предложение - особенность продукта, услуги или компании, которая отличает ее от конкурентов и представляет особую ценность для целевой аудитории. Используется в креативах и на посадочных страницах"},
            
            # Платформы
            {"term": "Яндекс.Директ", "definition": "Контекстная реклама от Яндекса с показом в поиске и на сайтах-партнерах"},
            {"term": "VK Реклама", "definition": "Реклама в социальной сети ВКонтакте с таргетингом по интересам"},
            {"term": "Telegram Ads", "definition": "Реклама в мессенджере Telegram с показом в каналах и ботах"},
            {"term": "MyTarget", "definition": "Рекламная платформа от VK с показом на сайтах-партнерах"},
            
            # Кампании
            {"term": "РКО кампании", "definition": "Рекламные кампании для продвижения расчетно-кассового обслуживания"},
            {"term": "РБИДОС кампании", "definition": "Рекламные кампании для продвижения расчетно-кассового обслуживания для ИП и физлиц"},
            {"term": "Бизнес-карты кампании", "definition": "Рекламные кампании для продвижения корпоративных банковских карт"},
            {"term": "Бизнес-кредиты кампании", "definition": "Рекламные кампании для продвижения кредитных продуктов для бизнеса"}
        ]
    
    def _build_index(self):
        """Создает векторный индекс"""
        if os.path.exists(self.index_file):
            print("🔄 Загрузка существующего индекса...")
            self.index = faiss.read_index(self.index_file)
            return
        
        print("🔄 Создание векторного индекса...")
        
        # Создаем тексты для эмбеддингов
        texts = []
        for item in self.knowledge_items:
            text = f"{item['term']} {item['definition']}"
            texts.append(text)
        
        # Создаем эмбеддинги
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Нормализуем для косинусного сходства
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        # Создаем FAISS индекс
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings.astype('float32'))
        
        # Сохраняем индекс
        faiss.write_index(self.index, self.index_file)
        print(f"✅ Индекс создан: {len(self.knowledge_items)} элементов")
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Семантический поиск"""
        # Создаем эмбеддинг для запроса
        query_embedding = self.model.encode([query])
        query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
        
        # Ищем похожие векторы
        similarities, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        # Возвращаем результаты
        results = []
        for idx, similarity in zip(indices[0], similarities[0]):
            if idx < len(self.knowledge_items):
                item = self.knowledge_items[idx].copy()
                item['similarity'] = float(similarity)
                results.append(item)
        
        return results
    
    def enhance_report(self, report: str, question: str) -> str:
        """Улучшает отчет с помощью векторного поиска"""
        results = self.search(question, top_k=2)
        
        if not results:
            return report
        
        enhanced = report + "\n\n📚 Контекстная информация:\n" + "-" * 40 + "\n"
        
        for item in results:
            enhanced += f"🔹 {item['term']}\n"
            enhanced += f"   {item['definition']}\n"
            enhanced += f"   📊 Релевантность: {item['similarity']:.2f}\n\n"
        
        return enhanced

# Тестирование
if __name__ == "__main__":
    print("🧪 Тестирование векторной RAG системы")
    rag = SimpleVectorRAG()
    
    test_queries = ["ДМИК", "AOV", "КИБ", "маркетинг", "СББОЛ"]
    
    for query in test_queries:
        print(f"\n🔍 Запрос: '{query}'")
        results = rag.search(query)
        
        if results:
            print(f"✅ Найдено {len(results)} результатов:")
            for item in results:
                print(f"   📝 {item['term']}: {item['definition'][:80]}...")
                print(f"   📊 Релевантность: {item['similarity']:.2f}")
        else:
            print("❌ Результаты не найдены")
    
    print("\n✅ Векторная RAG система готова!") 