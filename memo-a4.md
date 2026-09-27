# Mémo - Systèmes distribués et théorème CAP

**UE 1 · Chapitre 1** · une page, recto

## Le vocabulaire

| Terme | Sens |
| --- | --- |
| Nœud | une machine (ou un processus) du système |
| Réplication | plusieurs copies des **mêmes** données |
| Sharding | chaque machine porte un **sous-ensemble** des données |
| Timeout | fin de l'attente locale ; l'effet distant reste incertain |
| Idempotence | répéter la même demande garde le même effet métier |
| Partition réseau | des groupes de nœuds actifs ne communiquent plus |
| Linéarisabilité (C de CAP) | tout se passe comme sur une copie unique, dans l'ordre réel |
| Disponibilité (A de CAP) | toute requête reçue par un nœud en marche finit par aboutir |
| Cohérence à terme | sans nouvelle écriture, les copies finissent par converger |
| Majorité | plus de la moitié des nœuds : 2 sur 3, 3 sur 5 |

## CAP et PACELC

- **CAP** : pendant une partition, on ne garantit pas à la fois la
  linéarisabilité et la disponibilité de toutes les opérations.
- **PACELC** : **P**artition → **A** ou **C** ; **E**lse (sinon) →
  **L**atence ou **C**ohérence.
- Le choix se fait **par opération** : compteur indicatif PA/EL,
  confirmation d'une place PC/EC.

## Tester et attribuer en une seule opération

```sql
UPDATE places SET titulaire = 'alice'
WHERE concert = 'C17' AND place = 42 AND titulaire IS NULL;
-- UPDATE 1 : attribuée · UPDATE 0 : refus métier, déjà prise
```

## PostgreSQL : réplication

| Commande | Effet |
| --- | --- |
| `SELECT pg_is_in_recovery();` | `t` sur une copie, `f` sur le primaire |
| `SELECT application_name, sync_state FROM pg_stat_replication;` | sur le primaire : qui suit, en quel mode |
| `SELECT pg_wal_replay_pause();` / `pg_wal_replay_resume();` | sur la copie : suspendre ou reprendre l'application |
| `ALTER SYSTEM SET synchronous_standby_names = 'pg_b';` puis `SELECT pg_reload_conf();` | confirmer seulement après la copie |
| `SET synchronous_commit = remote_apply;` | attendre que la copie ait **appliqué** |
| `ALTER SYSTEM RESET synchronous_standby_names;` | revenir en asynchrone |
| `\timing on` | afficher la durée de chaque requête |

## etcd

```bash
etcdctl endpoint status --cluster -w table   # qui est leader, quel terme
etcdctl put CLE VALEUR
etcdctl get CLE                              # lecture linéarisable (majorité)
etcdctl get CLE --consistency=s              # lecture locale, peut être ancienne
```

## Docker

```bash
docker compose up -d --build      # démarrer
docker compose ps                 # état des machines
docker compose logs guichet       # journal d'une machine
docker compose exec pg-a psql     # entrer dans une machine
docker network disconnect ue1-interne pg-b   # partition
docker network connect ue1-interne pg-b      # fin de partition
docker compose down -v            # tout arrêter et effacer
```
