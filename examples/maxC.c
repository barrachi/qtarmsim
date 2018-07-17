#define TAM 5

int vec[TAM] = {10, -3, 47, 95, 8};

int main()
{
	register int max, tam, i, a;
	
	tam = TAM;
	i = 0;
	max = vec[i++];
	while(--tam) {
		a = vec[i++];
		if (max < a)
			max = a;
	}
	
	return max;
}

