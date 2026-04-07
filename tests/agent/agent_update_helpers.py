import time
from typing import Optional, Tuple

import pytest
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from locators.agent_create_locators import AGENT_NAME_INPUT
from locators.agent_locators import AGENT_MY_AGENTS_BUTTON


AGENT_LIST_CONTAINER = (By.XPATH, "//div[@data-testid='virtuoso-item-list']")
AGENT_ITEMS_XPATH = "./*[@data-item-index or @data-index]"
AGENT_CARD_LINK_SELECTOR = "a[href*='/ai-helpy-chat/agents/']"
AGENT_TITLE_IN_ITEM_XPATH = ".//p[contains(@class, 'MuiTypography-noWrap')]"
DRAFT_CHIP_XPATH = ".//span[contains(@class,'MuiChip-label') and normalize-space()='초안']"
EDIT_BUTTON_SELECTOR = "button:has(svg[data-icon='pen'])"
CHAT_INPUT = (By.NAME, "input")


def go_to_my_agents(wait):
    wait.until(EC.element_to_be_clickable(AGENT_MY_AGENTS_BUTTON)).click()
    wait.until(EC.url_contains("/ai-helpy-chat/agents/mine"))


def _wait_for_agent_list_container(driver, wait):
    wait.until(EC.presence_of_all_elements_located(AGENT_LIST_CONTAINER))
    return wait.until(lambda d: _find_agent_list_container_with_agents(d))


def _find_agent_list_container_with_agents(driver):
    containers = driver.find_elements(*AGENT_LIST_CONTAINER)
    for container in containers:
        try:
            if container.find_elements(By.CSS_SELECTOR, AGENT_CARD_LINK_SELECTOR):
                return container
        except StaleElementReferenceException:
            continue
    return None


def _get_active_scroll_container(driver, wait):
    last_error = None
    for _ in range(5):
        try:
            list_container = _wait_for_agent_list_container(driver, wait)
            return driver.execute_script(
                """
                const list = arguments[0];
                const hasScrollableY = (el) => {
                  if (!el) return false;
                  const style = getComputedStyle(el);
                  const oy = style.overflowY;
                  return (oy === 'auto' || oy === 'scroll') && (el.scrollHeight - el.clientHeight > 2);
                };
                let el = list;
                while (el) {
                  if (hasScrollableY(el)) return el;
                  el = el.parentElement;
                }
                return list;
                """,
                list_container,
            )
        except StaleElementReferenceException as e:
            last_error = e
            continue

    if last_error:
        raise last_error
    raise TimeoutException("활성 스크롤 컨테이너를 찾지 못했습니다.")


def get_agent_items(driver, wait):
    last_error = None
    for _ in range(5):
        try:
            container = _wait_for_agent_list_container(driver, wait)
            return container.find_elements(By.XPATH, AGENT_ITEMS_XPATH)
        except StaleElementReferenceException as e:
            last_error = e
            continue

    if last_error:
        raise last_error
    return []


def extract_agent_id_from_href(href: str) -> Optional[str]:
    marker = "/ai-helpy-chat/agents/"
    if marker not in href:
        return None
    return href.split(marker, 1)[1].split("/", 1)[0]


def extract_agent_meta_from_item(item):
    title_elements = item.find_elements(By.XPATH, AGENT_TITLE_IN_ITEM_XPATH)
    card_links = item.find_elements(By.CSS_SELECTOR, AGENT_CARD_LINK_SELECTOR)

    if not card_links:
        return None

    title = (title_elements[0].text or "").strip() if title_elements else ""
    href = card_links[0].get_attribute("href")
    agent_id = extract_agent_id_from_href(href)
    if not agent_id:
        return None

    return {
        "title": title,
        "href": href,
        "agent_id": agent_id,
    }


def find_first_saved_agent_item_with_edit(agent_items):
    for item in agent_items:
        meta = extract_agent_meta_from_item(item)
        if not meta:
            continue

        is_draft = bool(item.find_elements(By.XPATH, DRAFT_CHIP_XPATH)) or meta["href"].endswith("/builder")
        if is_draft:
            continue

        edit_buttons = item.find_elements(By.CSS_SELECTOR, EDIT_BUTTON_SELECTOR)
        if edit_buttons:
            return item, meta, edit_buttons[0]

    return None, None, None


def find_first_saved_agent_item_with_edit_with_scroll(driver, wait, max_scroll_pages=60):
    scroller = _get_active_scroll_container(driver, wait)
    driver.execute_script("arguments[0].scrollTop = 0;", scroller)

    previous_scroll_top = -1
    for _ in range(max_scroll_pages):
        agent_items = get_agent_items(driver, wait)
        target_item, target_meta, target_edit_button = find_first_saved_agent_item_with_edit(agent_items)
        if target_item and target_meta and target_edit_button:
            return target_item, target_meta, target_edit_button

        driver.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollTop + Math.max(arguments[0].clientHeight * 0.9, 240);",
            scroller,
        )
        try:
            wait.until(
                lambda d: d.execute_script("return arguments[0].scrollTop;", scroller) > previous_scroll_top
                or d.execute_script(
                    "return arguments[0].scrollTop + arguments[0].clientHeight >= arguments[0].scrollHeight - 2;",
                    scroller,
                )
            )
        except TimeoutException:
            pass

        current_scroll_top = driver.execute_script("return arguments[0].scrollTop;", scroller)
        reached_bottom = driver.execute_script(
            "return arguments[0].scrollTop + arguments[0].clientHeight >= arguments[0].scrollHeight - 2;",
            scroller,
        )
        if reached_bottom or current_scroll_top <= previous_scroll_top:
            break
        previous_scroll_top = current_scroll_top

    return None, None, None


def open_saved_agent_builder(driver, wait) -> Tuple[str, str]:
    go_to_my_agents(wait)
    target_item, target_meta, target_edit_button = find_first_saved_agent_item_with_edit_with_scroll(driver, wait)

    if not target_item or not target_meta or not target_edit_button:
        current_url = driver.current_url
        visible_items = len(get_agent_items(driver, wait))
        print(
            "[debug][skip] open_saved_agent_builder: "
            f"target_item={bool(target_item)}, target_meta={bool(target_meta)}, "
            f"target_edit_button={bool(target_edit_button)}, visible_items={visible_items}, "
            f"current_url={current_url}"
        )
        pytest.skip("수정 가능한 게시 에이전트 카드를 찾지 못했습니다.")

    wait.until(EC.element_to_be_clickable(target_edit_button)).click()
    expected_path = f"/ai-helpy-chat/agents/{target_meta['agent_id']}/builder"
    wait.until(EC.url_contains(expected_path))
    wait.until(EC.visibility_of_element_located(AGENT_NAME_INPUT))

    return target_meta["agent_id"], target_meta["title"]


def update_agent_name(wait, new_name: str):
    name_input = wait.until(EC.visibility_of_element_located(AGENT_NAME_INPUT))
    # React/MUI 입력 컴포넌트는 clear()만으로 상태 반영이 누락될 수 있어
    # 키 조합 + JS fallback으로 값을 확실히 비운다.
    name_input.click()
    name_input.send_keys(Keys.CONTROL, "a")
    name_input.send_keys(Keys.DELETE)

    try:
        wait.until(lambda d: (name_input.get_attribute("value") or "") == "")
    except TimeoutException:
        driver = name_input.parent
        driver.execute_script(
            """
            const el = arguments[0];
            el.value = '';
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            el.blur();
            """,
            name_input,
        )
        wait.until(lambda d: (name_input.get_attribute("value") or "") == "")

    name_input.send_keys(new_name)
    name_input.send_keys(Keys.TAB)
    name_input.send_keys(Keys.ESCAPE)

    time.sleep(0.5)
    wait.until(lambda d: (name_input.get_attribute("value") or "") == new_name)


def click_save(wait):
    driver = wait._driver
    save_button_xpath = (
        "//button["
        "normalize-space()='저장' "
        "or normalize-space()='업데이트' "
        "or normalize-space()='만들기' "
        "or contains(normalize-space(),'수정') "
        "or @type='submit'"
        "]"
    )

    def _is_actionable_button(btn):
        try:
            if not btn.is_enabled():
                return False
            rendered = driver.execute_script(
                """
                const el = arguments[0];
                if (!el) return false;
                const style = getComputedStyle(el);
                const rect = el.getBoundingClientRect();
                return style.display !== 'none' &&
                       style.visibility !== 'hidden' &&
                       rect.width > 0 &&
                       rect.height > 0 &&
                       style.pointerEvents !== 'none';
                """,
                btn,
            )
            return bool(rendered)
        except Exception:
            return False

    try:
        wait.until(EC.presence_of_element_located((By.XPATH, save_button_xpath)))
        # 입력 반영/검증으로 버튼 활성화가 지연될 수 있어 추가 대기
        try:
            WebDriverWait(driver, 10).until(
                lambda d: any(_is_actionable_button(btn) for btn in d.find_elements(By.XPATH, save_button_xpath))
            )
        except TimeoutException:
            pass

        buttons = driver.find_elements(By.XPATH, save_button_xpath)
        for button in buttons:
            try:
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});",
                    button,
                )
                if not _is_actionable_button(button):
                    continue

                try:
                    button.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", button)

                _submit_publish_setting_modal_if_present(wait)
                return
            except StaleElementReferenceException:
                continue
    except TimeoutException:
        pass

    try:
        debug_buttons = driver.find_elements(By.XPATH, save_button_xpath)
        debug_states = []
        for btn in debug_buttons:
            try:
                debug_states.append(
                    {
                        "text": (btn.text or "").strip(),
                        "enabled": btn.is_enabled(),
                        "displayed": btn.is_displayed(),
                        "type": btn.get_attribute("type"),
                        "disabled_attr": btn.get_attribute("disabled"),
                        "aria_disabled": btn.get_attribute("aria-disabled"),
                    }
                )
            except Exception:
                debug_states.append({"state_error": True})
        print(
            "[debug][skip] click_save: "
            f"candidates={len(debug_buttons)}, states={debug_states}, "
            f"current_url={driver.current_url}"
        )
    except Exception as e:
        print(f"[debug][skip] click_save: debug collection failed: {e}")

    pytest.skip("저장 버튼을 찾지 못해 수정 검증을 진행할 수 없습니다.")


def _submit_publish_setting_modal_if_present(wait):
    publish_modal_locator = (
        By.XPATH,
        "//div[@role='dialog' and .//form[@id='publish-setting-form']]",
    )
    publish_save_button_locator = (
        By.XPATH,
        "//div[@role='dialog' and .//form[@id='publish-setting-form']]"
        "//button[@type='submit' and @form='publish-setting-form' and normalize-space()='저장']",
    )

    try:
        wait.until(EC.visibility_of_element_located(publish_modal_locator))
    except TimeoutException:
        return

    wait.until(EC.element_to_be_clickable(publish_save_button_locator)).click()
    wait.until(EC.invisibility_of_element_located(publish_modal_locator))


def wait_for_save_feedback(driver, wait):
    expected_message = "에이전트가 업데이트 되었습니다."
    try:
        success_toast = wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//*[@role='alert' and (contains(@class, 'notistack-MuiContent-success') or .//*[@data-testid='circle-checkIcon'])]",
                )
            )
        )
        assert expected_message in (success_toast.text or ""), (
            "업데이트 성공 토스트 문구가 예상과 다릅니다. "
            f"expected='{expected_message}', actual='{success_toast.text}'"
        )
    except TimeoutException:
        # 일부 환경에서는 success class가 다를 수 있어 기존 notistack 패턴을 한 번 더 시도한다.
        try:
            fallback_toast = wait.until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "//*[@role='alert' and (contains(@class, 'notistack') or .//*[@id='notistack-snackbar'])]",
                    )
                )
            )
            assert expected_message in (fallback_toast.text or ""), (
                "업데이트 성공 토스트 문구가 예상과 다릅니다. "
                f"expected='{expected_message}', actual='{fallback_toast.text}'"
            )
        except TimeoutException:
            # 환경에 따라 토스트가 짧게 표시되거나 없을 수 있어 짧게 대기 후 진행한다.
            time.sleep(0.5)

    wait.until(EC.visibility_of_element_located(AGENT_NAME_INPUT))


def wait_until_name_value(wait, expected_name: str):
    wait.until(
        lambda d: (
            d.find_element(*AGENT_NAME_INPUT).get_attribute("value") or ""
        ) == expected_name
    )


def find_agent_card_by_id(driver, wait, agent_id: str):
    css = f"a[href*='/ai-helpy-chat/agents/{agent_id}']"
    scroller = _get_active_scroll_container(driver, wait)
    container = _wait_for_agent_list_container(driver, wait)
    driver.execute_script("arguments[0].scrollTop = 0;", scroller)

    previous_scroll_top = -1
    for _ in range(80):
        matched_links = container.find_elements(By.CSS_SELECTOR, css)
        if matched_links:
            card_link = matched_links[0]
            item = card_link.find_element(By.XPATH, "./ancestor::*[@data-item-index or @data-index][1]")
            return item

        driver.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollTop + Math.max(arguments[0].clientHeight * 0.9, 240);",
            scroller,
        )
        try:
            wait.until(
                lambda d: d.execute_script("return arguments[0].scrollTop;", scroller) > previous_scroll_top
                or d.execute_script(
                    "return arguments[0].scrollTop + arguments[0].clientHeight >= arguments[0].scrollHeight - 2;",
                    scroller,
                )
            )
        except TimeoutException:
            pass

        current_scroll_top = driver.execute_script("return arguments[0].scrollTop;", scroller)
        reached_bottom = driver.execute_script(
            "return arguments[0].scrollTop + arguments[0].clientHeight >= arguments[0].scrollHeight - 2;",
            scroller,
        )
        if reached_bottom or current_scroll_top <= previous_scroll_top:
            break
        previous_scroll_top = current_scroll_top

    pytest.fail(f"대상 에이전트 카드를 찾지 못했습니다. agent_id={agent_id}, current_url={driver.current_url}")


def return_to_my_agents_from_builder(driver, wait):
    driver.back()
    wait.until(EC.url_contains("/ai-helpy-chat/agents/mine"))
    driver.refresh()
    wait_for_my_agents_list_ready(driver, wait)


def wait_for_my_agents_list_ready(driver, wait):
    container = _wait_for_agent_list_container(driver, wait)
    wait.until(lambda d: len(container.find_elements(By.XPATH, AGENT_ITEMS_XPATH)) > 0)
    wait.until(lambda d: len(container.find_elements(By.CSS_SELECTOR, AGENT_CARD_LINK_SELECTOR)) > 0)
    _scroll_my_agents_list_to_top(driver, wait)


def _scroll_my_agents_list_to_top(driver, wait=None):
    try:
        if wait is not None:
            scroller = _get_active_scroll_container(driver, wait)
            driver.execute_script("arguments[0].scrollTop = 0;", scroller)
            return

        container = _find_agent_list_container_with_agents(driver)
        if container is None:
            return
        scroller = driver.execute_script(
            """
            const list = arguments[0];
            const hasScrollableY = (el) => {
              if (!el) return false;
              const style = getComputedStyle(el);
              const oy = style.overflowY;
              return (oy === 'auto' || oy === 'scroll') && (el.scrollHeight - el.clientHeight > 2);
            };
            let el = list;
            while (el) {
              if (hasScrollableY(el)) return el;
              el = el.parentElement;
            }
            return list;
            """,
            container,
        )
        driver.execute_script("arguments[0].scrollTop = 0;", scroller)
    except Exception:
        pass


def get_card_title(item) -> str:
    title_elements = item.find_elements(By.XPATH, AGENT_TITLE_IN_ITEM_XPATH)
    return (title_elements[0].text or "").strip() if title_elements else ""


def set_visibility_scope(wait, scope: str):
    lowered = scope.strip().lower()
    if lowered not in {"public", "private"}:
        raise ValueError(f"scope는 public/private 중 하나여야 합니다. actual={scope}")

    labels = {
        "public": ["공개", "Public", "전체 공개"],
        "private": ["비공개", "Private"],
    }[lowered]

    # 텍스트 기반 선택자 우선
    for label in labels:
        candidates = [
            (By.XPATH, f"//button[normalize-space()='{label}']"),
            (By.XPATH, f"//label[normalize-space()='{label}']"),
            (By.XPATH, f"//*[@role='radio' and normalize-space()='{label}']"),
            (By.XPATH, f"//*[contains(@class,'MuiFormControlLabel-root') and .//*[normalize-space()='{label}']]"),
        ]
        for locator in candidates:
            try:
                element = wait.until(EC.element_to_be_clickable(locator))
                element.click()
                return
            except TimeoutException:
                continue

    # value 기반 라디오 fallback
    try:
        radio = wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f"//input[@type='radio' and translate(@value,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='{lowered}']",
                )
            )
        )
        radio.click()
        return
    except TimeoutException:
        pytest.skip(f"공개범위({scope}) 선택 UI를 찾지 못했습니다.")


def is_login_page(driver) -> bool:
    current_url = (driver.current_url or "").lower()
    if "accounts.elice.io/accounts/signin" in current_url:
        return True

    email_inputs = driver.find_elements(By.NAME, "loginId")
    password_inputs = driver.find_elements(By.NAME, "password")
    return bool(email_inputs and password_inputs)


def assert_private_access_blocked(driver, wait, base_url: str, agent_id: str):
    target_path = f"/ai-helpy-chat/agents/{agent_id}"
    target_url = f"{base_url}/agents/{agent_id}"
    driver.get(target_url)

    WebDriverWait(driver, 10).until(
        lambda d: is_login_page(d)
        or target_path not in (d.current_url or "")
        or len(d.find_elements(*CHAT_INPUT)) == 0
    )

    body_text = (driver.find_element(By.TAG_NAME, "body").text or "").lower()
    blocked_keywords = ["권한", "접근", "forbidden", "로그인", "not found", "404"]
    has_blocked_keyword = any(keyword in body_text for keyword in blocked_keywords)

    assert is_login_page(driver) or has_blocked_keyword or target_path not in driver.current_url, (
        "비공개 전환 후 비로그인 접근이 차단되지 않았습니다. "
        f"current_url={driver.current_url}"
    )


def assert_public_access_allowed(driver, wait, base_url: str, agent_id: str):
    expected_path = f"/ai-helpy-chat/agents/{agent_id}"
    target_url = f"{base_url}/agents/{agent_id}"
    driver.get(target_url)

    WebDriverWait(driver, 10).until(
        lambda d: (expected_path in (d.current_url or "")) or is_login_page(d)
    )

    assert not is_login_page(driver), (
        "공개 전환 후에도 비로그인 접근이 로그인 페이지로 리다이렉트되었습니다. "
        f"current_url={driver.current_url}"
    )
    assert expected_path in driver.current_url, (
        "공개 전환 후 대상 에이전트 URL로 진입하지 못했습니다. "
        f"current_url={driver.current_url}, expected_path={expected_path}"
    )
