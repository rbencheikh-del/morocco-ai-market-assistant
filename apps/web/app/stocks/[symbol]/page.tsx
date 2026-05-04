import { StockDetailView } from "../../components/StockDetailView";
import { getStockDetailData } from "../../lib/api";

type Props = {
  params: Promise<{ symbol: string }>;
};

export default async function StockDetailPage({ params }: Props) {
  const { symbol } = await params;
  const data = await getStockDetailData(symbol);

  return <StockDetailView data={data} />;
}
