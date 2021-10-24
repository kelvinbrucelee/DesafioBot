import locale
import logging
import mysql.connector
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conecxão com banco de dados
db_connection = mysql.connector.connect(host="108.167.132.18", user="kelvin40_mvx", passwd="mvx1234",
                                        database="kelvin40_mvx")
cursor = db_connection.cursor()

def cliente(update: Update, context: CallbackContext) -> None:
    digitar = str(update.message.text).lower()
    comando, cliente = digitar.split(" ")
    sql = (f'SELECT vi.venda_id as venda, sum(valor * quantidade) as total FROM venda_itens '
           f'vi INNER JOIN (SELECT v.id as pedido, cliente_id, data FROM venda v WHERE  v.cliente_id = {cliente} ORDER BY '
           f'id DESC limit 1) h1 ON h1.pedido = vi.venda_id WHERE vi.venda_id;')
    cursor.execute(sql)
    conn = cursor.fetchall()

    # Codigo retorna valor total
    for venda in conn:
        if venda:
            ped = venda[0]
            total = venda[1]
            locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
            contotal = locale.currency(total, grouping=True, symbol=None)
            update.message.reply_text(f'PEDIDO: {ped}')
            update.message.reply_text(f'VALOR: {contotal} ')
            update.message.reply_text('ㅤㅤITEMㅤㅤ|ㅤQTDㅤ|ㅤVALOR')
            break
    sql = (f'SELECT vi.venda_id as pedido, nome as produto, quantidade, valor, sum(valor * quantidade) as soma, '
           f'h1.cliente_id as cli FROM venda_itens vi INNER JOIN produto on produto.id = vi.produto_id INNER JOIN ('
           f'SELECT v.id as ped, cliente_id, data FROM venda v WHERE  v.cliente_id = {cliente} ORDER BY id DESC limit 1)'
           f'h1 ON h1.ped = vi.venda_id WHERE vi.venda_id GROUP BY pedido, produto, valor, quantidade;')
    cursor.execute(sql)
    connection = cursor.fetchall()

    #Retorna os itens do pedido
    for produto in connection:
        nome = produto[1]
        prodnome = nome[:12]
        quantidade = produto[2]
        valor = produto[3]
        soma = valor * quantidade
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        convalor = locale.currency(soma, grouping=True, symbol=None)
        update.message.reply_text(f'{prodnome}| {quantidade}ㅤ| {convalor}')

def total(update: Update, context: CallbackContext) -> None:
    sql = (
        f'SELECT sum(valor * quantidade) as total FROM venda INNER JOIN venda_itens on venda.id = venda_itens.venda_id')
    cursor.execute(sql)
    connect = cursor.fetchall()
    for total in connect:
        tipo = total[0]
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        valor = locale.currency(tipo, grouping=True, symbol=None)
        update.message.reply_text(f'VALOR TOTAL DE TODAS AS VENAS: R$%s' % valor)

def mes(update: Update, context: CallbackContext) -> None:
    mesatual = datetime.today().strftime('%m')
    sql = (
        f'SELECT sum(valor * quantidade) as total, DATA FROM venda INNER JOIN venda_itens on venda.id = '
        f'venda_itens.venda_id WHERE MONTH(data) = {mesatual}')
    cursor.execute(sql)
    con = cursor.fetchall()
    for total in con:
        tipo = total[0]
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        valor = locale.currency(tipo, grouping=True, symbol=None)
        update.message.reply_text(f'VALOR TOTAL DE TODAS AS VENDAS DO MÊS ATUAL: R$%s' % valor)

def echo(update: Update, context: CallbackContext) -> None:
    texto = """
        ESCOLHA UMA OPÇÃO A BAIXO
        /TOTAL - TOTAL DE VENDAS
        /MES - TOTAL DE VENDAS DO 
        MÊS ATUAL
        CLIENTE - DIGITE /CLIENTE E O ID 
        DO CLIENTE
        EXEMPLO: /CLIENTE 12345"""
    update.message.reply_text(texto)

def main() -> None:
    updater = Updater("2025925571:AAHvKCZ5E6oOA8ZSDWxdJrb9QBbbFpXAJig")

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("cliente", cliente))
    dispatcher.add_handler(CommandHandler("total", total))
    dispatcher.add_handler(CommandHandler("mes", mes))

    # mensagem - ecoa a mensagem no telegrama
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

db_connection.close()
