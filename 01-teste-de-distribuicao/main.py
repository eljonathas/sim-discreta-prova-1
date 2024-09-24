import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats

dados = {
    'Caixa 1 (Sequencial)': [5.5, 8.2, 4.3, 9.0, 6.7, 9.8, 5.9, 10.5, 7.3, 8.7],
    'Caixa 2 (Simultâneo)': [4.0, 5.8, 3.2, 6.5, 4.7, 6.9, 4.1, 7.3, 5.5, 6.4]
}

df = pd.DataFrame(dados)

caixa1 = df['Caixa 1 (Sequencial)']
caixa2 = df['Caixa 2 (Simultâneo)']

shapiro_caixa1 = stats.shapiro(caixa1)
shapiro_caixa2 = stats.shapiro(caixa2)

normalidade_caixa1 = shapiro_caixa1.pvalue > 0.05
normalidade_caixa2 = shapiro_caixa2.pvalue > 0.05

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

stats.probplot(caixa1, dist="norm", plot=ax1)
ax1.set_title("Q-Q Plot - Caixa 1 (Sequencial)")

stats.probplot(caixa2, dist="norm", plot=ax2)
ax2.set_title("Q-Q Plot - Caixa 2 (Simultâneo)")

plt.tight_layout()
plt.show()