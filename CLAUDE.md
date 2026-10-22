# EC物販MVP

海外の卸サイト（7s goodなど）で小ロットを仕入れ、Amazon.co.jpで販売する事業のMVP。進め方は `docs/roadmap.md`、販売戦略は `docs/strategy.md`（評価と座組の見直しは `docs/strategy-review.md`）、判定基準は `docs/criteria.md`、ブランドの定義は `data/brand.md` を正とする。

**基本指針：** `docs/hurdles.md` を最上位の判断基準とする。①検証 → ②自走 → ③安定の3段階を、実績の事業利益と実質時給で判定する。合格ラインの数値はパラメータとして `config/assumptions.toml` で管理し、状況に応じて見直す。ただし、判定期間の途中や判定の直後に、未達を合格にするために合格ラインを下げてはならない。拡大・撤退の提案は、必ず現在の段階に照らして行う。

**販売戦略：** 特定のドメインに集中してシェアを取り、そのあと隣接するドメインに広げる。候補はすべて、決裁済みのドメインの中から選ぶ。

## 役割分担
- **人間**：決裁（お金を使う判断）、実物の品質確認、法的な最終判断、出品の公開承認
- **エージェント**：調査、試算、原稿作成、監視。人間のゲートを越える行動（発注、出品の公開、セラーセントラルの操作）は行わない

## エージェント
| 名前 | 担当 | 状態 |
|---|---|---|
| market-researcher | 候補の洗い出し | 稼働可 |
| sourcing-evaluator | 粗利試算・規制チェック・決裁用の提案書 | 稼働可 |
| listing-creator | 出品原稿・画像加工の指示 | 稼働可（商品確定後に使う） |
| sales-operator / accountant | 価格・在庫の運用、粗利レポート | Phase 2で構築（小口の間はレポートCSVを集計） |

標準の流れ：`/domain-selection` でドメインを決める（初回のみ）→ `/sourcing-cycle <テーマ>` で market-researcher → sourcing-evaluator → 決裁依頼まで一括実行 → 人間が `data/decisions.md` に決裁を記録 → サンプル検品後に listing-creator

## コマンド
- 粗利計算：`python3 tools/profit_calc.py data/candidates.csv`
- ハードル判定（月次）：`python3 tools/hurdle_check.py`（`data/monthly.csv` に実績を記入してから）
- 作業時間の記録：`data/timelog.csv`（日付、時間、作業内容）
- テスト：`python3 -m unittest discover -s tests`
