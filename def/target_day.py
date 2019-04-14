import time
import datetime
import jpholiday #祝日判定ライブラリ

#検索対象日をリストのリストで返す関数
#delta　は何日先までを対象にするか
#args　は対象曜日(0：月曜～6：日曜、7：祝日)

def day(delta, args):
    today = datetime.date.today()
    start_date = today + datetime.timedelta(days=2)
    end_date = today + datetime.timedelta(days=delta)

    d = start_date
    delta = datetime.timedelta(days=1)
    t_days = []#今月用
    while d <= end_date:
        weekday = d.weekday()
        #if weekday == 5 or weekday == 6 or jpholiday.is_holiday(d) == True:#「土」「日」「祝」
        if 7 in args:
            if weekday in args or jpholiday.is_holiday(d) == True:
                #t_days.append("{},{},{}".format(d.year, d.month, d.day))
                t_days.append(d)
        else:
            if weekday in args:
                #t_days.append("{},{},{}".format(d.year, d.month, d.day))
                t_days.append(d)
        d += delta
    return t_days

if __name__ == "__main__":
    t_days = day(30, [5,6,7])
    print(t_days)
    print(type(t_days[0]))
