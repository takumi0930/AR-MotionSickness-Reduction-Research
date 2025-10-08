total_sickness_score_child = 9
not_experienced_child = 0
msa = total_sickness_score_child * 9 / (9 - not_experienced_child)

total_sickness_score_adult = 14
not_experienced_adult = 0
msb = total_sickness_score_adult * 9 / (9 - not_experienced_adult)

x = msa + msb

a = 5.1160923
b = -0.055169904
c = -0.00067784495
d = 0.000010714752

y = a*x + b*(x**2) + c*(x**3) + d*(x**4)

print(msa)
print(msb)
print(x)
print(y)