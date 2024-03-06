from googletrans import Translator

translator = Translator()

print(translator.translate(text="what is your name", dest='hi'))

a = translator.detect("")

print(a)