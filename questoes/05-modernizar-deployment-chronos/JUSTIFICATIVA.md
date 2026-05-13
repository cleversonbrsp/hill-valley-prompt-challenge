# Justificativa — B-A-B (Questão 05)

**Before:** o prompt inclui o manifest legado completo como estado inicial inequívoco (“Treat it as the exact before state”).

**After:** a lista “Modernize…” define o estado desejado (HA, imagem versionada, secrets externos, resources, probes, securityContext, labels, estratégia de rollout, PDB opcional).

**Bridge:** a instrução “You are the on-call Kubernetes engineer…” + regras de manter `name/namespace` salvo necessidade conecta o antes/depois com o processo GitOps e o formato final (apenas YAML em fences).
