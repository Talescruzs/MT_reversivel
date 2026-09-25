# Máquina de Turing Reversivel -> Maria Rita, Nathalia, Sofia e Tales 
## Máquina de Turing 
modelo matemático composto por uma fita divida em células, um cabeçote de leitura e escrita e um conjunto finito de estados. A partir de cada estado atual e do símbolo lido, a máquina escreve um novo símbolo, move o cabeçote para esquerda ou direita e passa para um novo estado. No arquivo de entrada, cada transição é representada no formato (q,a) = (p,b,D). 
  
É uma <b>MT reversível</b> quando cada configuração possui no máximo uma configuração predecessora, ou seja, sempre podemos determinar, de forma única, o passo anterior, propriedade que as MT não possuem em geral, já que descartam informação durante a execução. Na máquina exemplo, as transições (2,1) = (4,X,L) e (3,0) = (4,X,L) levam ao mesmo estado e escrevem o mesmo símbolo. Assim, ao encontrar um X no estado 4, não é possível determinar se o símbolo original era 0 ou 1. 
  
A relevância decorre do princípio de Landauer, onde a eliminação de informação implica uma dissipação mínima de energia. Então, uma computação que não descarta informação, em princípio, pode ser realizada com menor gasto energético. Bennet demonstrou que toda MT pode ser simulada por uma MT reversível. Ele utilizou três fitas e é executada em três etapas. 
  * Na primeira, a máquina original é executada na fita de trabalho e, a cada passo, a transição aplicada é registrada na fita de histórico.
  * Na segunda, o resultado é copiado para a fita de saída.
  * Na terceira, o histórico é percorrido em ordem inversa cada transição é desfeita, sendo seu registro removido.
    
Ao final, a fita de trabalho contém novamente a entrada original, a fita de histórico vazia e a fita de saída contém o resultado, sem nenhuma informação perdida. O custo é o espaço adicional necessário para armazenar o histórico durante a execução. A máquina do 'entrada-quíntupla.txt' reconhece palavras com a mesma quantidade de símbolos 0 e 1. Para a entrada 0011, a primeira etapa executa 15 transições, deixa a fita de trabalho com conteúdo $XXX e registra 15 entradas no histórico.  Na segunda etapa, esse conteúdo é copiado para a fita de saída. Na terceira, as 15 transições são desfeitas. A fita de trabalho retorna ao conteúdo original 0011 e a palavra é aceita.

## Sobre o código
