from random import randint
from typing import Any, List

from src.model.manual_parser import FunctionPrototype


class ToolExecutor:
    def __init__(self) -> None:
        pass

    def __call__(self, func_name: str, **kwargs) -> Any:
        func = getattr(self, func_name)
        return func(**kwargs)

    def execute(self, function: FunctionPrototype) -> Any:
        func_name = function.function_name
        kwargs = function.kwargs
        return self(func_name, **kwargs)

    def execute_all(self, functions: List[FunctionPrototype]) -> Any:
        # For now only works with one function properly
        if not functions:
            return None
        res = None
        for f in functions:
            res = self.execute(f)
        return res

    def change_phone_number(self, phone_number: str) -> str:
        if self._check_multi_acc():
            return "Замечена множественная регистрация. " \
                   "Пожалуйста, обратитесь на нашу почту help@example.com" \
                   "и прикрепите в письме ваши документы (перечень док-ов). Вам помогут сменить номер телефона."

        return "Ваш номер телефона успешно изменен. (Вызов функции смены номера телефона)"

    def _check_multi_acc(self) -> bool:
        num = randint(0, 9)
        if num >= 5:
            return True

        return False

    def get_cashback_amount(self, uid: str) -> int:
        return randint(0, 278)


if __name__ == "__main__":
    x = ToolExecutor()
    print(x("change_phone_number", phone_number="1234567"))
    print(x("get_cashback_amount", uid="12345678"))
