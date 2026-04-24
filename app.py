import streamlit as st
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta

date = datetime.date.today()

def calculate(sum: float, percent: float, period: int, type: str): 
    """Формирует график платежей и параметры кредита в зависимости от выбранного графика

    Формулы для дифференцированного график:
		sum_per_month = sum / n
        sum_of_interest = sum * per_month_interest
		где,
		sum - сумма займа,
		per_month_interest =  percent/100/12 - месячная процентная ставка,
		n - срок кредитования (в месяцах).
  
	Формула ежемесячного платежа для аннуитетного график:
		monthly_payment = sum * (per_month_interest + per_month_interest / ((1 + per_month_interest)^n - 1))
		где,
		sum - сумма займа,
		per_month_interest =  percent/100/12 - месячная процентная ставка,
		n - срок кредитования (в месяцах).

	Args:
		sum: Сумма кредита.
		percent: Ставка (%).
		period: Срок кредитования в месяцах.
        type: Тип графика.

	Returns:
		График платежей, полную сумму платежей, ежемесячный платеж для аннуитетного графика
	"""
    schedule = []
    per_month_interest = percent / 100 / 12 #месячная процентная ставка
    monthly_payment = None # На случай дифференцированного графика
    if type == "Дифференцированный график":
        sum_per_month = round(sum / period) #Долговая часть ежемесячного платежа
        for month in range(period):
            sum_of_interest = round(sum * per_month_interest) #Проценты
            payment = {}
            payment["Месяцы"] = date + relativedelta(months=month)
            payment["Остаток долга"] = sum
            payment["Платеж"] = sum_per_month + sum_of_interest
            payment["Процентная часть"] = sum_of_interest
            payment["Долговая часть"] = sum_per_month
            if month != period - 1:
                payment["Остаток долга на конец периода"] = sum - sum_per_month
            else:
                payment["Остаток долга на конец периода"] = 0
            schedule.append(payment)
            sum -= sum_per_month
        
    if type == "Аннуитетный график":
        if per_month_interest == 0:
            multiplayer = 1/period
        else:
            multiplayer = (per_month_interest + (per_month_interest / ((1 + per_month_interest) ** period - 1)))
        monthly_payment = round(sum * multiplayer)
        for month in range(period):
            payment = {}
            payment["Дата платежа"] = date + relativedelta(months=month) 
            payment["Остаток долга"] = sum
            payment["Процентная часть"] = round(sum * per_month_interest)
            if month != period - 1:
                payment["Платеж"] = monthly_payment
                payment["Долговая часть"] = round(monthly_payment - sum * per_month_interest)
                payment["Остаток долга на конец периода"] = round(sum - (monthly_payment - sum * per_month_interest))
            else:
                payment["Платеж"] = sum + round(sum * per_month_interest)
                payment["Долговая часть"] = 0
                payment["Остаток долга на конец периода"] = 0
            schedule.append(payment)
            sum = round(sum - (monthly_payment - sum * per_month_interest))
    table = pd.DataFrame(schedule)
    full_pay = table["Платеж"].sum()
    return table, full_pay, monthly_payment
    
st.markdown(
    "<h1><b><center>Кредитный калькулятор</center></b></h1>",
    unsafe_allow_html=True
)

col1, col2 = st.columns([0.6, 0.4])
with col1:
    cred_sum = st.number_input("Сумма кредита, руб", min_value=1000, 
                               max_value=100000000, step=1000, value=300000, 
                               help="Максимальная сумма кредита 10 млн.руб., минимальная сумма кредита 1 тыс.руб."
                               )
    percent = st.number_input("Ставка, %.", min_value=0.0, max_value=25.0, 
                              step=0.1, value=15.0,
                              help="Ставка должна быть от 0% (расстрочка) до 25%"
                              )
    period = st.slider("Срок кредита, месяцев:", 1, 240 , 60, 1, 
                       help="Срок кредита, не может быть меньше 1 месаца и больше 20 лет"
                       )
    options = ["Дифференцированный график", "Аннуитетный график"]
    type = st.radio(
        "Выберите график:", 
        options,
        help = 'Аннуитетный — равные платежи; '
            'Дифференцированный — платежи уменьшаются со временем'
        )
    # Защита от обхода ограничений элементов streamlit
    if cred_sum <= 0 or cred_sum > 10000000:
        st.error('Сумма должна быть от 1000 до 10000000')
    if percent < 0 or percent > 25:
        st.error('Процентная ставка должна быть в диапазоне 0-25%')   
    if period < 1 or period > 240:
        st.error('Период кредитования должен быть от 1 месяца до 20 лет')   
    if date <  datetime.date.today():
        st.error('Дата не может быть меньше текущей')
         
    is_pressed = st.button("📊 Показать график платежей")
    
table,full_pay, monthly_payment = calculate(cred_sum, percent, period, type) 

with col2:
    today = datetime.date.today()
    last_day = datetime.date(today.year, 12, 31)
    date = st.date_input(
        "Желаемая дата первого платежа",
        format = "DD.MM.YYYY",
        value = today,
        min_value = today,
        max_value = last_day,
    )
    with st.expander("Общие данные по кредиту",True):
        st.write(f"Сумма кредита: **{cred_sum} руб.**")
        st.write(f"Вы заплатите: **{full_pay} руб.**")
        st.write(f"Переплата составит: **{full_pay - cred_sum} руб.**")
    if monthly_payment != None:
        st.write("Ежемесячный платеж составляет:")
        st.write(f"**{monthly_payment} руб.**")      
                          
if is_pressed:
        st.dataframe(table, hide_index=True, width=2000)