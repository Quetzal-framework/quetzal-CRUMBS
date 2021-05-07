import re

def nb_species_posterior_probabilities(bpp_output):
    p = re.compile('P\[(\d)\] = (\d+\.\d+)')
    iterator = p.finditer(bpp_output)
    posterior=dict();
    for match in iterator:
        posterior[int(match.group(1))] = float(match.group(2))
    return posterior
