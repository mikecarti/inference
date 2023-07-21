from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import fitz


class ReceiptOCR:
    """
    Class for getting text info from checks or receipts by OCR
    """

    def __init__(self):
        """
        Note that the first time you use easyocr lib on you machine
        the pytorch model will be downloaded
        """
        # self.reader = easyocr.Reader(['ru', 'en'], gpu=False, )
        self.reader = None
        self.temp_doc_file_path = f"data/temp_doc/temp_receipt.pdf"
        self.prompt_template = """
        На вход тебе будет дана информация с банковского чека.
        Твоя задача - описать главную информацию и определить, успешно ли прошла транзакция.
        
        Пример: 
        Аггрегируя информацию заметил, что
        Сумма перевода: "указанное кол-во рублей в оплате"
        Комиссия: "указанная комиссия"
        Карта отправителя: "указанная карта"
        Банк получателя: "указанный банк"
        ФИО отправителя: "указанное фио отправителя"
        ФИО получателя: "указанное фио получателя"
        Номер операции: "указанный номер операции"
        Номер телефона получателя: "указанный номер получателя"
        Дата и время: "Указанные дата и время"
        Другие данные: "Остальные важные данные, если таковые имеются"
        
        Вердикт: транзакция прошла "успешно/ не успешно"
        
        Информация с чека: 
        {check}
        
        Ответ:
        Аггрегируя информацию заметил, что
        Вердикт: транзакция прошла...
        """
        self.chain = LLMChain(
            llm=ChatOpenAI(temperature=0),
            prompt=PromptTemplate(template=self.prompt_template, input_variables=["check"]))

    def check_transactions_status(self, doc):
        """
        This method uses LLM to work with text.
        Feel free to change self.prompt_template for your needs.
        """
        self._asave_temp_doc(doc)
        text = self._pdf2text()
        return self.chain.run(check=text)

    async def acheck_transactions_status(self, doc):
        """
        This method uses LLM to work with text.
        Feel free to change self.prompt_template for your needs.
        """
        await self._asave_temp_doc(doc)
        text = self._pdf2text()
        return await self.chain.arun(check=text)

    def read_text(self, img, concat: bool = True) -> str:
        """
        This method reads image (which can be given as bytes or file path)
        and returns text from this image.
        """
        result = self.reader.readtext(img)
        words = [result[i][1] for i in range(len(result))]
        if concat:
            return "".join(w + ',' for w in words)

        return words

    def _pdf2text(self):
        with fitz.open(self.temp_doc_file_path) as doc:
            check_page = doc.load_page(0)
            text = check_page.get_text()
        return text

    async def _asave_temp_doc(self, doc):
        await doc.download(
            destination_file=self.temp_doc_file_path,
        )
