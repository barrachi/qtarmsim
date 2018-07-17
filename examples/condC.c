#define TAM 1

#define UMBMAS		10
#define UMBMENOS	-10

volatile int vec[TAM] = {-45};

int main()
{
	register int vali, valo;
	
	vali = vec[0];
	if (vali > UMBMAS)
		valo = UMBMAS;
	else if (vali < UMBMENOS)
		valo = UMBMENOS;
	else valo = vali;	
	
	return valo;
}

