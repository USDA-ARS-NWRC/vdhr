#! /usr/bin/awk -f

BEGIN {
	ex_max = 1.75
	exr = 0.75
	ex_min = 1.0
	c1_min = 0.026
	c1_max = 0.069
	c1r = 0.043
	Tmin = -10.0
	Tmax = 0.0
	Tz = 0.0
	Tr0 = 0.5
	Pcr0 = 0.25
	Pc0 = 0.75
	
	water = 1000.0

	print "Tpp\tpp\tswe\t%sno\trho-ns\tdrho-c\tdrho-m\trho-s\trho\tzs\n"
}
NR == 1  &&  NF == 1  &&  $1 == "help" {
	print "Estimates static new snow density (kg/m^3) from"
	print "precipitation temperature (C) and mass (kg or mm m^2)"
	print "accounting for overburden (depth),"
	print "and temperature metamorphism compaction."
	print "After Anderson (1976), Kojima (1967), Mellor (1964) & Yoshida (1963)"
	print "usage: rhosx < {Tpp pp}"
	exit 1
}
{
# set precipitation temperature, % snow, and SWE
	if ($1 < Tmin)
		Tpp = Tmin
	else {
		Tpp = $1
		if (Tpp > Tmax)
			tsnow = Tmax
		else
			tsnow = Tpp
	}

	if (Tpp <= -0.5)
		pcs = 1.0
	else if ((Tpp > -0.5) && (Tpp <= 0.0))
		pcs = (((-Tpp) / Tr0) * Pcr0) + Pc0
	else if ((Tpp > 0.0) && (Tpp <= (Tmax +1.0)))
		pcs = (((-Tpp) / (Tmax + 1.0)) * Pc0) + Pc0
 	else 
		pcs = 0.0

	pp = $2
	swe = pp * pcs

	if (swe > 0 ) {

# new snow density - no compaction
		Trange = Tmax - Tmin
		ex = ex_min + (((Trange + (tsnow - Tmax)) / Trange) * exr)

		if(ex > ex_max)
			ex = ex_max

		rho_ns = (50 + (1.7 * (((Tpp - Tz) + 15)^ex))) / water

# proportional total storm mass compaction
		d_rho_c = (0.026 * exp(-0.08 * (Tz - tsnow)) * swe * exp(-21.0 * rho_ns))

		if ((rho_ns * water) < 100.0)
			c11 = 1.0
		else
			c11 = exp(-0.046 * ((rho_ns * water) - 100.0))

		d_rho_m = 0.01 * c11 * exp(-0.04 * (Tz - tsnow))

# compute snow denstiy, depth & combined liquid and snow density
		rho_s = rho_ns +((d_rho_c + d_rho_m) * rho_ns)

		zs = swe / rho_s

		if (swe < pp) {
			if (pcs > 0.0)
				rho = (pcs * rho_s) + (1 - pcs)
			if (rho > 1.0)
				rho = water / water
		} else
			rho = rho_s
	} else {
		rho_ns = 0.0
		d_rho_m = 0.0
		d_rho_c = 0.0
		zs = 0.0
		rho_s = 0.0
		rho = water / water
	}
# convert densities from proportions, to kg/m^3 or mm/m^2
	rho_ns *= water
	d_rho_c *= water
	d_rho_m *= water
	rho_s *= water
	rho *= water

# print results
	printf "%.1f\t%.1f\t%.1f\t%.2f\t%.0f\t%.2f\t%.2f\t%.0f\t%.0f\t%.1f\n", Tpp, pp, swe, pcs, rho_ns, d_rho_c, d_rho_m, rho_s, rho, zs
}
