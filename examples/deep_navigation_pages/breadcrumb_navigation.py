"""
Страницы Amazon с breadcrumb навигацией - отслеживание пути и истории переходов.
Каждая страница знает, откуда пришел пользователь и может предоставить детальную информацию о пути.
"""

from selenium.webdriver.common.by import By
import logging
from datetime import datetime
from page_object_library import BasePage, Button, Input, BaseElement, auto_log


class BreadcrumbBasePage(BasePage):
    """Базовая страница с отслеживанием breadcrumb навигации"""

    def __init__(self, driver, base_url=None, timeout=10, driver_name="default"):
        super().__init__(driver, base_url, timeout, driver_name)
        self.navigation_history = []
        self.navigation_timestamps = []
        self.navigation_metadata = {}

    def add_to_navigation_history(self, page_name, metadata=None):
        """Добавляет страницу в историю навигации"""
        timestamp = datetime.now()

        self.navigation_history.append(page_name)
        self.navigation_timestamps.append(timestamp)

        if metadata:
            self.navigation_metadata[page_name] = metadata

        logging.info(f"📍 Добавлено в историю: {page_name} ({timestamp.strftime('%H:%M:%S')})")

    @auto_log
    def get_navigation_path(self):
        """Возвращает полный путь навигации"""
        if not self.navigation_history:
            return "Начальная страница"

        return " → ".join(self.navigation_history)

    @auto_log
    def get_navigation_summary(self):
        """Возвращает детальную сводку навигации"""
        if not self.navigation_history:
            return {
                'path': "Начальная страница",
                'steps': 0,
                'duration': '0s',
                'current_page': self.__class__.__name__
            }

        total_duration = (self.navigation_timestamps[-1] - self.navigation_timestamps[0]).total_seconds()

        return {
            'path': self.get_navigation_path(),
            'steps': len(self.navigation_history),
            'duration': f"{total_duration:.1f}s",
            'current_page': self.__class__.__name__,
            'start_time': self.navigation_timestamps[0].strftime('%H:%M:%S'),
            'end_time': self.navigation_timestamps[-1].strftime('%H:%M:%S'),
            'metadata': self.navigation_metadata
        }

    @auto_log
    def breadcrumb_navigate_to(self, target_page_class, reason=None):
        """Навигация с отслеживанием breadcrumb"""
        current_page_name = self.__class__.__name__
        metadata = {'reason': reason} if reason else None
        self.add_to_navigation_history(current_page_name, metadata)

        target_page = self.navigate_to(target_page_class)

        if hasattr(target_page, 'navigation_history'):
            target_page.navigation_history = self.navigation_history.copy()
            target_page.navigation_timestamps = self.navigation_timestamps.copy()
            target_page.navigation_metadata = self.navigation_metadata.copy()

        return target_page

    @auto_log
    def get_previous_page(self):
        """Возвращает информацию о предыдущей странице"""
        if len(self.navigation_history) < 2:
            return None

        return {
            'page': self.navigation_history[-2],
            'timestamp': self.navigation_timestamps[-2],
            'metadata': self.navigation_metadata.get(self.navigation_history[-2], {})
        }

    @auto_log
    def can_go_back(self):
        """Проверяет, можно ли вернуться назад"""
        return len(self.navigation_history) > 1


class BreadcrumbAmazonLoginPage(BreadcrumbBasePage):
    """Страница входа с breadcrumb отслеживанием"""
    DEFAULT_URL = "/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_custrec_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"

    def _init_elements(self):
        self.username_input = Input(self, (By.ID, "ap_email"), "Поле ввода email")
        self.continue_button = Button(self, (By.ID, "continue"), "Кнопка продолжить")
        self.password_input = Input(self, (By.ID, "ap_password"), "Поле ввода пароля")
        self.sign_in_button = Button(self, (By.ID, "signInSubmit"), "Кнопка входа")

    @auto_log
    def login(self, email, password):
        """Выполняет вход с отслеживанием"""
        self.username_input.type(email)
        self.continue_button.click()
        self.password_input.type(password)
        self.sign_in_button.click()

        return self.breadcrumb_navigate_to(
            BreadcrumbAmazonHomePage,
            reason="Successful login"
        )


class BreadcrumbAmazonHomePage(BreadcrumbBasePage):
    """Главная страница с breadcrumb"""
    DEFAULT_URL = "/"

    def _init_elements(self):
        self.account_menu = BaseElement(self, (By.ID, "nav-link-accountList"), "Меню аккаунта")
        self.search_input = Input(self, (By.ID, "twotabsearchtextbox"), "Поле поиска")

    @auto_log
    def go_to_account(self):
        """Переход к аккаунту с отслеживанием"""
        self.account_menu.click()
        return self.breadcrumb_navigate_to(
            BreadcrumbAmazonAccountPage,
            reason="Access account settings"
        )

    @auto_log
    def get_home_navigation_info(self):
        """Получает информацию о навигации на главной странице"""
        summary = self.get_navigation_summary()
        summary['page_type'] = 'Home'
        summary['available_actions'] = ['go_to_account', 'search', 'browse_categories']
        return summary


class BreadcrumbAmazonAccountPage(BreadcrumbBasePage):
    """Страница аккаунта с детальным отслеживанием"""
    DEFAULT_URL = "/gp/css/homepage.html"

    def _init_elements(self):
        self.digital_services_link = BaseElement(
            self,
            (By.XPATH, "//a[contains(@href, 'nodeId=200127470')]"),
            "Ссылка на цифровые сервисы"
        )
        self.back_to_home = BaseElement(self, (By.ID, "nav-logo"), "Возврат на главную")

    @auto_log
    def go_to_digital_services(self):
        """Переход к цифровым сервисам с отслеживанием"""
        self.digital_services_link.click()

        return self.breadcrumb_navigate_to(
            BreadcrumbAmazonDigitalServicesPage,
            reason="Access device support"
        )

    @auto_log
    def go_to_home(self):
        """Возврат домой с отслеживанием"""
        self.back_to_home.click()
        return self.breadcrumb_navigate_to(
            BreadcrumbAmazonHomePage,
            reason="Return to home from account"
        )

    @auto_log
    def get_account_navigation_analytics(self):
        """Получает аналитику навигации по аккаунту"""
        summary = self.get_navigation_summary()
        previous = self.get_previous_page()

        analytics = {
            'navigation_summary': summary,
            'came_from': previous['page'] if previous else 'Direct access',
            'time_since_previous': None,
            'suggested_next_actions': ['go_to_digital_services', 'manage_devices', 'view_orders']
        }

        if previous and len(self.navigation_timestamps) >= 2:
            time_diff = (self.navigation_timestamps[-1] - self.navigation_timestamps[-2]).total_seconds()
            analytics['time_since_previous'] = f"{time_diff:.1f}s"

        return analytics


class BreadcrumbAmazonDigitalServicesPage(BreadcrumbBasePage):
    """Страница цифровых сервисов с breadcrumb"""
    DEFAULT_URL = "/gp/help/customer/display.html?nodeId=200127470"

    def _init_elements(self):
        self.fire_tablets_link = BaseElement(
            self,
            (By.XPATH, "//a[contains(@href, 'nodeId=GJDXXK9NZ6FMB8PJ')]"),
            "Ссылка на Fire Tablets"
        )
        self.back_to_account = BaseElement(
            self,
            (By.XPATH, "//a[contains(@href, 'css/homepage')]"),
            "Возврат к аккаунту"
        )

    @auto_log
    def go_to_fire_tablets(self):
        """Переход к Fire Tablets с отслеживанием"""
        self.fire_tablets_link.click()

        return self.breadcrumb_navigate_to(
            BreadcrumbAmazonFireTabletsPage,
            reason="Access Fire Tablet support"
        )

    @auto_log
    def go_to_account(self):
        """Возврат к аккаунту с отслеживанием"""
        self.back_to_account.click()
        return self.breadcrumb_navigate_to(
            BreadcrumbAmazonAccountPage,
            reason="Return to account from digital services"
        )


class BreadcrumbAmazonFireTabletsPage(BreadcrumbBasePage):
    """Страница Fire Tablets с расширенным breadcrumb"""
    DEFAULT_URL = "/gp/help/customer/display.html?nodeId=GJDXXK9NZ6FMB8PJ"

    def _init_elements(self):
        self.wifi_help_link = BaseElement(
            self,
            (By.XPATH, "//a[contains(@href, 'nodeId=GZFJ72443RVDHEFQ')]"),
            "Ссылка на помощь WiFi"
        )
        self.back_to_digital_services = BaseElement(
            self,
            (By.XPATH, "//a[contains(@href, 'nodeId=200127470')]"),
            "Возврат к цифровым сервисам"
        )

    @auto_log
    def go_to_wifi_help(self):
        """Переход к WiFi помощи с отслеживанием"""
        self.wifi_help_link.click()

        return self.breadcrumb_navigate_to(
            BreadcrumbAmazonWifiHelpPage,
            reason="Access WiFi troubleshooting"
        )

    @auto_log
    def go_to_digital_services(self):
        """Возврат к цифровым сервисам с отслеживанием"""
        self.back_to_digital_services.click()
        return self.breadcrumb_navigate_to(
            BreadcrumbAmazonDigitalServicesPage,
            reason="Return to digital services from tablets"
        )

    @auto_log
    def get_tablet_support_journey(self):
        """Получает информацию о пути поддержки планшетов"""
        summary = self.get_navigation_summary()

        journey_info = {
            'support_path': summary,
            'depth_level': len(self.navigation_history),
            'time_to_reach_tablets': summary['duration'],
            'recommended_next_step': 'go_to_wifi_help if connectivity issues',
            'alternative_paths': ['go_back_to_account', 'search_for_specific_issue']
        }

        return journey_info


class BreadcrumbAmazonWifiHelpPage(BreadcrumbBasePage):
    """Страница WiFi помощи с полным breadcrumb отслеживанием"""
    DEFAULT_URL = "/gp/help/customer/display.html?nodeId=GZFJ72443RVDHEFQ"

    def _init_elements(self):
        self.wifi_instructions = BaseElement(
            self,
            (By.XPATH, "//span[contains(text(), 'Access internet by following these steps')]"),
            "Инструкции WiFi"
        )
        self.back_to_fire_tablets = BaseElement(
            self,
            (By.XPATH, "//a[contains(@href, 'nodeId=GJDXXK9NZ6FMB8PJ')]"),
            "Возврат к Fire Tablets"
        )

    @auto_log
    def get_wifi_instructions(self):
        """Получает инструкции WiFi"""
        return self.wifi_instructions.get_text()

    @auto_log
    def verify_wifi_instructions_present(self):
        """Проверяет наличие инструкций WiFi"""
        instructions = self.get_wifi_instructions()
        return "internet" in instructions.lower() or "connect" in instructions.lower()

    @auto_log
    def go_to_fire_tablets(self):
        """Возврат к Fire Tablets с отслеживанием"""
        self.back_to_fire_tablets.click()
        return self.breadcrumb_navigate_to(
            BreadcrumbAmazonFireTabletsPage,
            reason="Return from WiFi help to tablets"
        )

    @auto_log
    def get_wifi_instructions_with_journey_info(self):
        """Получает инструкции WiFi с полной информацией о пути"""
        instructions = self.get_wifi_instructions()
        navigation_summary = self.get_navigation_summary()

        journey_analysis = self._analyze_user_journey()

        return {
            'wifi_instructions': instructions,
            'navigation_journey': navigation_summary,
            'journey_analysis': journey_analysis,
            'success_metrics': {
                'reached_target': True,
                'steps_taken': len(self.navigation_history),
                'total_time': navigation_summary['duration'],
                'efficiency_score': self._calculate_efficiency_score()
            }
        }

    def _analyze_user_journey(self):
        """Анализирует путь пользователя для оптимизации"""
        if len(self.navigation_history) == 0:
            return {'journey_type': 'direct_access', 'optimization_potential': 'none'}

        expected_path = [
            'BreadcrumbAmazonLoginPage',
            'BreadcrumbAmazonHomePage',
            'BreadcrumbAmazonAccountPage',
            'BreadcrumbAmazonDigitalServicesPage',
            'BreadcrumbAmazonFireTabletsPage',
            'BreadcrumbAmazonWifiHelpPage'
        ]

        journey_analysis = {
            'journey_type': 'standard',
            'deviations': [],
            'optimization_suggestions': [],
            'user_behavior_insights': {}
        }

        if len(self.navigation_history) > len(expected_path):
            journey_analysis['journey_type'] = 'exploratory'
            journey_analysis['deviations'].append('extra_navigation_steps')
            journey_analysis['optimization_suggestions'].append('Consider direct links to WiFi help')

        if len(self.navigation_timestamps) > 1:
            transition_times = []
            for i in range(1, len(self.navigation_timestamps)):
                diff = (self.navigation_timestamps[i] - self.navigation_timestamps[i - 1]).total_seconds()
                transition_times.append(diff)

            avg_transition_time = sum(transition_times) / len(transition_times)
            journey_analysis['user_behavior_insights']['avg_transition_time'] = f"{avg_transition_time:.1f}s"

            if avg_transition_time > 10:
                journey_analysis['optimization_suggestions'].append('Pages may need clearer navigation cues')

        return journey_analysis

    def _calculate_efficiency_score(self):
        """Вычисляет оценку эффективности навигации"""
        if len(self.navigation_history) == 0:
            return 100

        optimal_steps = 5  # Login → Home → Account → Digital → Tablets → WiFi
        actual_steps = len(self.navigation_history)

        step_efficiency = max(0, 100 - (actual_steps - optimal_steps) * 10)

        if len(self.navigation_timestamps) > 1:
            total_time = (self.navigation_timestamps[-1] - self.navigation_timestamps[0]).total_seconds()
            optimal_time = 30

            if total_time <= optimal_time:
                time_efficiency = 100
            else:
                time_efficiency = max(0, 100 - (total_time - optimal_time) * 2)
        else:
            time_efficiency = 100

        overall_efficiency = (step_efficiency + time_efficiency) / 2
        return round(overall_efficiency, 1)

    @auto_log
    def get_breadcrumb_navigation_report(self):
        """Генерирует полный отчет о breadcrumb навигации"""
        navigation_summary = self.get_navigation_summary()
        journey_analysis = self._analyze_user_journey()
        efficiency_score = self._calculate_efficiency_score()

        report = {
            'report_generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'final_destination': 'Amazon WiFi Help Page',
            'navigation_summary': navigation_summary,
            'journey_analysis': journey_analysis,
            'performance_metrics': {
                'efficiency_score': efficiency_score,
                'total_steps': len(self.navigation_history),
                'total_duration': navigation_summary['duration'],
                'average_step_time': self._get_average_step_time()
            },
            'user_experience_insights': {
                'journey_complexity': 'High' if len(self.navigation_history) > 6 else 'Medium' if len(
                    self.navigation_history) > 3 else 'Low',
                'likely_user_satisfaction': 'High' if efficiency_score > 80 else 'Medium' if efficiency_score > 60 else 'Low',
                'recommended_improvements': journey_analysis.get('optimization_suggestions', [])
            },
            'breadcrumb_trail': " → ".join(self.navigation_history) if self.navigation_history else "Direct access"
        }

        return report

    def _get_average_step_time(self):
        """Вычисляет среднее время между шагами"""
        if len(self.navigation_timestamps) < 2:
            return "N/A"

        total_time = (self.navigation_timestamps[-1] - self.navigation_timestamps[0]).total_seconds()
        steps = len(self.navigation_timestamps) - 1
        return f"{total_time / steps:.1f}s"

    @auto_log
    def create_navigation_visualization(self):
        """Создает текстовую визуализацию пути навигации"""
        if not self.navigation_history:
            return "📍 Direct access to WiFi Help"

        visualization = "🗺️  Navigation Journey:\n"
        visualization += "=" * 50 + "\n"

        for i, (page, timestamp) in enumerate(zip(self.navigation_history, self.navigation_timestamps)):
            icon = self._get_page_icon(page)
            time_str = timestamp.strftime('%H:%M:%S')

            reason = self.navigation_metadata.get(page, {}).get('reason', 'Navigation')

            visualization += f"{i + 1:2d}. {icon} {page.replace('BreadcrumbAmazon', '').replace('Page', '')}\n"
            visualization += f"    🕐 {time_str} | 💭 {reason}\n"

            if i < len(self.navigation_history) - 1:
                visualization += "    ⬇️\n"

        visualization += "\n" + "=" * 50
        visualization += f"\n🎯 Final destination: WiFi Help"
        visualization += f"\n⏱️  Total journey time: {self.get_navigation_summary()['duration']}"
        visualization += f"\n📊 Efficiency score: {self._calculate_efficiency_score()}/100"

        return visualization

    def _get_page_icon(self, page_name):
        """Возвращает иконку для типа страницы"""
        icons = {
            'BreadcrumbAmazonLoginPage': '🔐',
            'BreadcrumbAmazonHomePage': '🏠',
            'BreadcrumbAmazonAccountPage': '👤',
            'BreadcrumbAmazonDigitalServicesPage': '💻',
            'BreadcrumbAmazonFireTabletsPage': '📱',
            'BreadcrumbAmazonWifiHelpPage': '📶'
        }
        return icons.get(page_name, '📄')


class BreadcrumbNavigationAnalyzer:
    """Анализатор паттернов breadcrumb навигации"""

    def __init__(self):
        self.session_data = []

    def add_navigation_session(self, wifi_help_page):
        """Добавляет сессию навигации для анализа"""
        if hasattr(wifi_help_page, 'get_navigation_summary'):
            session_summary = wifi_help_page.get_navigation_summary()
            self.session_data.append(session_summary)

    def analyze_navigation_patterns(self):
        """Анализирует паттерны навигации"""
        if not self.session_data:
            return "No navigation data available"

        total_sessions = len(self.session_data)
        avg_steps = sum(session['steps'] for session in self.session_data) / total_sessions

        paths = [session['path'] for session in self.session_data]
        path_frequency = {}
        for path in paths:
            path_frequency[path] = path_frequency.get(path, 0) + 1

        most_common_path = max(path_frequency.items(), key=lambda x: x[1])

        analysis = {
            'total_sessions_analyzed': total_sessions,
            'average_navigation_steps': round(avg_steps, 1),
            'most_common_path': most_common_path[0],
            'path_frequency': most_common_path[1],
            'optimization_recommendations': []
        }

        if avg_steps > 6:
            analysis['optimization_recommendations'].append("Consider adding direct links to reduce navigation steps")

        if path_frequency[most_common_path[0]] / total_sessions > 0.8:
            analysis['optimization_recommendations'].append(
                "Most users follow the same path - consider streamlining this journey")

        return analysis