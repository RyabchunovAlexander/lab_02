from streamstats.analysis import LogMetrics
from streamstats.models import LogLine


def test_metrics_empty_init():
    """Проверка, что при создании объекта все счетчики равны нулю."""
    metrics = LogMetrics()
    report = metrics.get_report_data()

    assert report["total_count"] == 0
    assert report["first_timestamp"] is None
    assert report["last_timestamp"] is None
    assert report["level_counts"] == {}
    assert report["top_sources"] == {}


def test_metrics_total_and_levels():
    """Тест правильности подсчета общего количества и распределения по уровням."""
    metrics = LogMetrics()

    # Корректно передаем объекты LogLine для инкремента счетчиков
    metrics.update(LogLine("2026-10-10T10:00:00Z", "INFO", "app", "Msg 1"))
    metrics.update(LogLine("2026-10-10T10:01:00Z", "DEBUG", "web", "Msg 2"))
    metrics.update(LogLine("2026-10-10T10:02:00Z", "INFO", "db", "Msg 3"))

    report = metrics.get_report_data()
    assert report["total_count"] == 3
    assert report["level_counts"]["INFO"] == 2
    assert report["level_counts"]["DEBUG"] == 1


def test_metrics_timestamps_order():
    """Проверка фиксации первой и последней временной метки лога."""
    metrics = LogMetrics()

    metrics.update(LogLine("2026-10-10T08:00:00Z", "INFO", "srv", "Start"))
    metrics.update(LogLine("2026-10-10T09:00:00Z", "WARNING", "srv", "Middle"))
    metrics.update(LogLine("2026-10-10T10:00:00Z", "ERROR", "srv", "End"))

    report = metrics.get_report_data()
    # Первая метка должна зафиксироваться, а последняя — перезаписаться в конце
    assert report["first_timestamp"] == "2026-10-10T08:00:00Z"
    assert report["last_timestamp"] == "2026-10-10T10:00:00Z"


def test_metrics_top_sources_only_errors():
    """Проверка, что в Top-5 источников попадают только ERROR и CRITICAL."""
    metrics = LogMetrics()

    metrics.update(LogLine("2026-10-10T12:00:00Z", "INFO", "clean_source", "Игнорируем"))
    metrics.update(LogLine("2026-10-10T12:01:00Z", "ERROR", "bad_source", "Считаем"))
    metrics.update(LogLine("2026-10-10T12:02:00Z", "CRITICAL", "worst_source", "Считаем"))

    report = metrics.get_report_data()
    # Источник со статусом INFO не должен учитываться в статистике ошибок
    assert "clean_source" not in report["top_sources"]
    assert report["top_sources"]["bad_source"] == 1
    assert report["top_sources"]["worst_source"] == 1


def test_metrics_top_sources_limit_five():
    """Проверка ограничения среза списка источников строго до Топ-5 элементов."""
    metrics = LogMetrics()

    # Генерируем 7 разных ошибочных источников логов
    for i in range(1, 8):
        for _ in range(i):  # Чем больше индекс, тем больше ошибок
            metrics.update(LogLine("2026-10-10T12:00:00Z", "ERROR", f"src_{i}", "Err"))

    report = metrics.get_report_data()
    # В словаре должно остаться строго 5 записей, а самые редкие (src_1, src_2) отсекаются
    assert len(report["top_sources"]) == 5
    assert "src_7" in report["top_sources"]
    assert "src_1" not in report["top_sources"]


def test_metrics_deterministic_sorting():
    """Жесткий тест детерминированной сортировки источников по алфавиту при равном количестве."""
    metrics = LogMetrics()

    # Добавляем одинаковое количество ошибок для разных по алфавиту источников
    metrics.update(LogLine("2026-10-10T12:00:00Z", "ERROR", "C_source", "Err"))
    metrics.update(LogLine("2026-10-10T12:00:00Z", "ERROR", "A_source", "Err"))
    metrics.update(LogLine("2026-10-10T12:00:00Z", "ERROR", "B_source", "Err"))

    report = metrics.get_report_data()
    # Превращаем ключи в список, чтобы проверить строгий порядок следования строк
    sources_order = list(report["top_sources"].keys())

    # Порядок должен стать алфавитным: A, B, C
    assert sources_order == ["A_source", "B_source", "C_source"]


def test_metrics_deterministic_sorting_mixed():
    """Тест сортировки, когда у источников разное количество, но у некоторых они равны."""
    metrics = LogMetrics()

    # У "X" — 3 ошибки, у "C" и "A" — по 2 ошибки (равенство)
    metrics.update(LogLine("2026-10-10T12:00:00Z", "ERROR", "C", "Err"))
    metrics.update(LogLine("2026-10-10T12:00:00Z", "ERROR", "C", "Err"))
    metrics.update(LogLine("2026-10-10T12:00:00Z", "ERROR", "X", "Err"))
    metrics.update(LogLine("2026-10-10T12:00:00Z", "ERROR", "X", "Err"))
    metrics.update(LogLine("2026-10-10T12:00:00Z", "ERROR", "X", "Err"))
    metrics.update(LogLine("2026-10-10T12:00:00Z", "ERROR", "A", "Err"))
    metrics.update(LogLine("2026-10-10T12:00:00Z", "ERROR", "A", "Err"))

    report = metrics.get_report_data()
    sources_order = list(report["top_sources"].keys())

    # X идет первым (count=3), а равные А и С сортируются по алфавиту (count=2)
    assert sources_order == ["X", "A", "C"]


def test_metrics_same_timestamps():
    """Тест работы с логами, у которых абсолютно одинаковые временные метки."""
    metrics = LogMetrics()

    metrics.update(LogLine("2026-10-10T15:00:00Z", "INFO", "app", "M1"))
    metrics.update(LogLine("2026-10-10T15:00:00Z", "INFO", "app", "M2"))

    report = metrics.get_report_data()
    # Начало и конец лога должны совпасть
    assert report["first_timestamp"] == "2026-10-10T15:00:00Z"
    assert report["last_timestamp"] == "2026-10-10T15:00:00Z"


def test_metrics_level_case_insensitivity_prevention():
    """Убеждаемся, что разные регистры строк уровней обрабатываются как независимые ключи."""
    metrics = LogMetrics()

    metrics.update(LogLine("2026-10-10T12:00:00Z", "INFO", "src", "Msg"))
    metrics.update(LogLine("2026-10-10T12:00:00Z", "ERROR", "src", "Msg"))

    report = metrics.get_report_data()
    assert "INFO" in report["level_counts"]
    assert "info" not in report["level_counts"]


def test_metrics_data_isolation():
    """Проверка независимости данных между двумя разными объектами анализаторов."""
    analyzer_1 = LogMetrics()
    analyzer_2 = LogMetrics()

    analyzer_1.update(LogLine("2026-10-10T12:00:00Z", "INFO", "src", "Msg"))

    # Данные из первого анализатора не должны перетекать во второй объект
    assert analyzer_1.total_count == 1
    assert analyzer_2.total_count == 0