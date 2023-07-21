import easyocr
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
        self.reader = easyocr.Reader(['ru', 'en'], gpu=False)
        self.prompt_template = """
        На вход тебе будет дана информация с банковского чека.
        Твоя задача - определить, успешно ли прошла транзакция.
        Информация с чека: 
        {check}
        """
        self.chain = LLMChain(
            llm=ChatOpenAI(temperature=0),
            prompt=PromptTemplate(template=self.prompt_template, input_variables=["check"]))

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

    def _pdf2img(self, filepath: str):
        """
        This method converts PDF to image.
        Since we doing it only for pdf check file
        we need to read only zero page ('cause check contains only one page)
        Note that this method returns bytes.
        """
        with fitz.open(filepath) as doc:
            check_page = doc.load_page(0)
            pixmap = check_page.get_pixmap(dpi=300)

        return pixmap.tobytes()

    def check_transactions_status(self, filepath: str):
        """
        This method uses LLM to work with text.
        Feel free to change self.prompt_template for your needs.
        """
        img = self._pdf2img(filepath)
        text = self.read_text(img)
        return self.chain.run(check=text)
    
    async def acheck_transactions_status(self, filepath: str):
        """
        This method uses LLM to work with text.
        Feel free to change self.prompt_template for your needs.
        """
        img = self._pdf2img(filepath)
        text = self.read_text(img)
        return await self.chain.arun(check=text)


if __name__ == "__main__":
    ocr = ReceiptOCR()
    print(ocr.check_transactions_status("Receipt.pdf"))