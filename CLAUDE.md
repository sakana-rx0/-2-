# EC物販MVP

海外の卸サイト（7s goodなど）で小ロットを仕入れ、Amazon.co.jpで販売する事業のMVP。進め方は `docs/roadmap.md`、判定基準は `docs/criteria.md` を正とする。

## 役割分担
- **人間**：決裁（お金を使う判断）、実物の品質確認、法的な最終判断、出品の公開承認
- **エージェント**：調査、試算、原稿作成、監視。人間のゲートを越える行動（発注、出品の公開、セラーセントラルの操作）は行わない

## エージェント
| 名前 | 担当 | 状態 |
|---|---|---|
| market-researcher | 候補の洗い出し | 稼働可 |
| sourcing-evaluator | 粗利試算・規制チェック・決裁用の提案書 | 稼働可 |
| listing-creator | 出品原稿・画像加工 | Phase 1で構築 |
| sales-operator / accountant | 価格・在庫の運用、粗利レポート | Phase 2で構築（小口の間はレポートCSVを集計） |

標準の流れ：market-researcher → sourcing-evaluator → 人間の決裁

## コマンド
- 粗利計算：`python3 tools/profit_calc.py data/candidates.csv`
- テスト：`python3 -m unittest discover -s tests`
