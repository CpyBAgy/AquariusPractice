"""
Тесты для трех подходов глубокой навигации:
1. Обычная последовательная навигация
2. Умная навигация с автоматическим поиском пути
3. Декораторная автоматическая навигация
4. Breadcrumb навигация с отслеживанием истории
"""

import logging

# Импорты для обычной навигации
from examples.deep_navigation_pages.straight_navigation import (
    AmazonLoginPage,
    AmazonHomePage,
)

# Импорты для умной навигации
from examples.deep_navigation_pages.smart_navigation import (
    SmartAmazonHomePage,
    SmartAmazonWifiHelpPage
)

# Импорты для декораторной навигации
from examples.deep_navigation_pages.decorator_navigation import (
    DecoratorAmazonHomePage,
)

# Импорты для breadcrumb навигации
from examples.deep_navigation_pages.breadcrumb_navigation import (
    BreadcrumbAmazonHomePage,
)


def test_regular_deep_navigation_full_path(page_factory):
    """
    Тест полного пути обычной навигации:
    Login → Home → Account → Digital Services → Fire Tablets → WiFi Help
    """
    logging.info("=== Тест обычной последовательной навигации ===")

    login_page = page_factory.create_page(AmazonLoginPage)
    login_page.open()

    home_page = login_page.login("vancous220@gmail.com", "MyStrongPassword")
    logging.info("✅ Переход: Login → Home")

    account_page = home_page.go_to_account()
    logging.info("✅ Переход: Home → Account")

    digital_services_page = account_page.go_to_digital_services()
    logging.info("✅ Переход: Account → Digital Services")

    fire_tablets_page = digital_services_page.go_to_fire_tablets()
    logging.info("✅ Переход: Digital Services → Fire Tablets")

    wifi_help_page = fire_tablets_page.go_to_wifi_help()
    logging.info("✅ Переход: Fire Tablets → WiFi Help")

    assert wifi_help_page.verify_wifi_instructions_present(), "WiFi инструкции не найдены"
    logging.info("✅ Найдены инструкции: 'Access internet by following these steps'")

    instructions = wifi_help_page.get_wifi_instructions()
    assert len(instructions) > 0, "Инструкции пусты"
    logging.info(f"📋 Инструкции получены: {instructions[:50]}...")

    logging.info("✅ Тест обычной навигации завершен успешно")


def test_smart_navigation_direct_path(page_factory):
    """
    Тест умной навигации - прямой переход к WiFi Help
    Система должна автоматически найти оптимальный путь
    """
    logging.info("=== Тест умной навигации - прямой путь ===")

    home_page = page_factory.create_page(SmartAmazonHomePage)
    home_page.open()

    wifi_help_page = home_page.smart_navigate_to(SmartAmazonWifiHelpPage)

    current_page_type = wifi_help_page.get_current_page_type()
    expected_types = ["SmartAmazonWifiHelpPage", "UnknownPage"]
    assert current_page_type in expected_types, f"Неожиданный тип страницы: {current_page_type}"

    assert wifi_help_page.verify_wifi_instructions_present(), "WiFi инструкции не найдены"

    logging.info("✅ Умная навигация успешно выполнила прямой переход")


def test_decorator_automatic_navigation(page_factory):
    """
    Тест автоматической навигации через декораторы
    Методы должны автоматически навигировать к нужной странице
    """
    logging.info("=== Тест декораторной автоматической навигации ===")

    home_page = page_factory.create_page(DecoratorAmazonHomePage)
    home_page.open()

    instructions = home_page.get_wifi_instructions_from_home()

    assert instructions is not None, "Декоратор не вернул инструкции"
    assert len(instructions) > 0, "Инструкции пусты"

    logging.info("✅ Декоратор автоматически выполнил навигацию к WiFi Help")
    logging.info(f"📋 Получены инструкции: {instructions[:50]}...")


def test_breadcrumb_navigation_with_history_tracking(page_factory):
    """
    Тест breadcrumb навигации с детальным отслеживанием истории
    """
    logging.info("=== Тест breadcrumb навигации с отслеживанием истории ===")

    home_page = page_factory.create_page(BreadcrumbAmazonHomePage)
    home_page.open()

    account_page = home_page.go_to_account()
    digital_services_page = account_page.go_to_digital_services()
    fire_tablets_page = digital_services_page.go_to_fire_tablets()
    wifi_help_page = fire_tablets_page.go_to_wifi_help()

    journey_info = wifi_help_page.get_wifi_instructions_with_journey_info()

    assert 'navigation_journey' in journey_info, "Отсутствует информация о пути"
    assert 'success_metrics' in journey_info, "Отсутствуют метрики успеха"

    navigation_summary = journey_info['navigation_journey']
    success_metrics = journey_info['success_metrics']

    assert success_metrics['reached_target'] == True, "Цель не достигнута"
    assert success_metrics['steps_taken'] > 0, "Шаги не отслежены"

    logging.info(f"📊 Путь навигации: {navigation_summary['path']}")
    logging.info(f"⏱️ Время: {navigation_summary['duration']}")

