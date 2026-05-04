const { useMemo, useState } = React;

const gradeStyles = {
  A: { trust: "Trustworthy", status: "TRUSTWORTHY", tone: "#7A2F1D" },
  B: { trust: "Good", status: "TRUSTWORTHY", tone: "#A84324" },
  C: { trust: "Caution", status: "CAUTION", tone: "#C45A2E" },
  D: { trust: "Suspicious", status: "CAUTION", tone: "#D87C3E" },
  F: { trust: "High Risk", status: "HIGH RISK", tone: "#7A2F1D" }
};

const sampleProduct = {
  product: {
    title: "Skechers Men Summits Brisbane Sneakers",
    brand: "Visit the Skechers Store",
    asin: "B0BQHQ2QGZ",
    price: "Rs. 2,515",
    old_price: "Rs. 4,299",
    discount: "-41%",
    rating: 4.1,
    reviews_count: 2439,
    bought_last_month: "200+ bought in past month",
    stock: "In stock",
    thumbnails: [
      "https://m.media-amazon.com/images/I/81XlIoVdx2L._SL1500_.jpg",
      "https://m.media-amazon.com/images/I/819SDEyN6QL._SL1500_.jpg",
      "https://m.media-amazon.com/images/I/61ztnRaeAVL._SL1500_.jpg"
    ],
    delivery: ["FREE delivery Sunday, 3 May", "Fastest delivery Tomorrow, 2 May"],
    product_details: {
      colour: "LIGHT GRAY",
      style_name: "Sneaker",
      closure_type: "Lace-Up",
      sport_type: "Walking",
      shoe_type: "Athletic Shoe",
      insole_cushioning: "Memory foam",
      sole_material: "Rubber",
      item_weight: "300 g",
      country_of_origin: "India",
      date_first_available: "19 December 2022"
    }
  },
  ratings_breakdown: {
    summary_text:
      "Customers find these sneakers comfortable, lightweight, and good value. They like the soft cushioning and balanced fit. Some report durability concerns, especially the insole coming out after limited use."
  },
  reviews: [
    {
      position: 1,
      title: "Super Comfortable & Amazingly Lightweight Sneakers",
      rating: 5,
      date: "28 September 2025",
      author: "milan",
      verified_purchase: true,
      helpful_votes: "7 people found this helpful",
      text:
        "Absolutely loved this product! The quality exceeded my expectations and delivery was super fast.",
      prediction: {
        final_label: "REAL",
        final_confidence: 0.7255,
        top_indicators: [
          { word: "delivery", score: 1 },
          { word: "product", score: 0.778 },
          { word: "fast", score: 0.7302 },
          { word: "quality", score: 0.6863 }
        ],
        full_token_map: [
          { word: "Absolutely", score: 0.6507 },
          { word: "loved", score: 0.4446 },
          { word: "this", score: 0.3563 },
          { word: "product", score: 0.778 },
          { word: "!", score: 0.4236 },
          { word: "The", score: 0.3001 },
          { word: "quality", score: 0.6863 },
          { word: "exceeded", score: 0.4408 },
          { word: "my", score: 0.4669 },
          { word: "expectations", score: 0.6149 },
          { word: "and", score: 0.426 },
          { word: "delivery", score: 1 },
          { word: "was", score: 0.4961 },
          { word: "super", score: 0.6166 },
          { word: "fast", score: 0.7302 },
          { word: ".", score: 0.2674 }
        ]
      }
    },
    {
      position: 2,
      title: "Okay Product",
      rating: 3,
      date: "15 January 2026",
      author: "saif ali shaikh",
      verified_purchase: true,
      helpful_votes: "One person found this helpful",
      text: "Product is good but the insole comes out. The glue is not good enough to hold it for long.",
      prediction: {
        final_label: "REAL",
        final_confidence: 0.8421,
        top_indicators: [{ word: "insole", score: 0.91 }, { word: "glue", score: 0.77 }],
        full_token_map: [
          { word: "Product", score: 0.55 },
          { word: "is", score: 0.2 },
          { word: "good", score: 0.48 },
          { word: "but", score: 0.7 },
          { word: "the", score: 0.2 },
          { word: "insole", score: 0.91 },
          { word: "comes", score: 0.62 },
          { word: "out", score: 0.58 },
          { word: ".", score: 0.15 }
        ]
      }
    },
    {
      position: 3,
      title: "Good quality and comfortable shoes",
      rating: 5,
      date: "14 January 2026",
      author: "Sanjay",
      verified_purchase: true,
      helpful_votes: null,
      text: "The item is original and of very good quality. Design and finishing are neat and packaging was secure.",
      prediction: {
        final_label: "FAKE",
        final_confidence: 0.6712,
        top_indicators: [{ word: "original", score: 0.84 }, { word: "quality", score: 0.78 }],
        full_token_map: [
          { word: "The", score: 0.32 },
          { word: "item", score: 0.41 },
          { word: "is", score: 0.25 },
          { word: "original", score: 0.84 },
          { word: "and", score: 0.28 },
          { word: "quality", score: 0.78 },
          { word: ".", score: 0.18 }
        ]
      }
    }
  ],
  purchase_options: {
    single_offer: { price: "Rs. 2,515.00", stock: "In stock", delivery: ["FREE delivery Sunday, 3 May"] }
  },
  similar_products: [
    { title: "Skechers Men Modern Cool Sneakers", price: "Rs. 2,758.00", rating: 4, reviews: 907 },
    { title: "Skechers Men Lace Up Sneaker Shoes", price: "Rs. 2,685.00", rating: 4.2, reviews: 501 },
    { title: "Skechers Men Summits Sneakers", price: "Rs. 2,490.00", rating: 4.1, reviews: 822 }
  ]
};

const textOnlySample = {
  prediction: "FAKE",
  confidence: 0.9982,
  important_words: [
    { word: "product", score: 0.9843 },
    { word: "!!!", score: 0.8686 },
    { word: "buy", score: 0.7736 },
    { word: "amazing", score: 0.6474 },
    { word: "quality", score: 0.6302 }
  ],
  full_token_map: [
    { word: "This", score: 0.4106 },
    { word: "product", score: 0.9843 },
    { word: "is", score: 0.3613 },
    { word: "absolutely", score: 0.4743 },
    { word: "amazing", score: 0.6474 },
    { word: "!", score: 0.5794 },
    { word: "I", score: 0.3312 },
    { word: "have", score: 0.2811 },
    { word: "never", score: 0.424 },
    { word: "seen", score: 0.5265 },
    { word: "anything", score: 0.3981 },
    { word: "like", score: 0.5217 },
    { word: "it", score: 0.3582 },
    { word: "before", score: 0.508 },
    { word: ".", score: 0.3497 },
    { word: "Must", score: 0.5473 },
    { word: "buy", score: 0.7736 },
    { word: "for", score: 0.5333 },
    { word: "everyone", score: 0.5547 },
    { word: "!!!", score: 0.8686 }
  ]
};

function sampleForMode(mode) {
  if (mode !== "text") return sampleProduct;
  return {
    ...sampleProduct,
    reviews: sampleProduct.reviews.map((review, index) => ({
      ...review,
      text:
        index === 0
          ? "This product is absolutely amazing! I have never seen anything like it before. It works perfectly and the quality is outstanding. Must buy for everyone!!!"
          : review.text,
      prediction: index === 0 ? textOnlySample : {
        prediction: review.prediction.final_label,
        confidence: review.prediction.final_confidence,
        important_words: review.prediction.top_indicators || [],
        full_token_map: review.prediction.full_token_map || []
      }
    }))
  };
}

const pages = [
  { id: "ensemble-product", title: "Full Analysis" },
  { id: "text-product", title: "Text Analysis" },
  { id: "manual", title: "Manual Review" }
];

const detailKeys = [
  "brand",
  "model_name",
  "colour",
  "color",
  "style_name",
  "shoe_type",
  "sport_type",
  "closure_type",
  "insole_cushioning",
  "material_type",
  "sole_material",
  "item_weight",
  "country_of_origin",
  "date_first_available",
  "warranty_description",
  "screen_size",
  "memory_storage_capacity"
];

function valueOrDash(value) {
  return value === null || value === undefined || value === "" ? "-" : value;
}

function getLabel(prediction) {
  return prediction?.final_label || prediction?.prediction || "PENDING";
}

function getConfidence(prediction) {
  return prediction?.final_confidence ?? prediction?.confidence ?? null;
}

function getFakeProbability(prediction) {
  if (!prediction) return null;
  if (prediction.fake_probability !== undefined) return Number(prediction.fake_probability);
  const confidence = getConfidence(prediction);
  if (confidence === null) return null;
  return getLabel(prediction) === "FAKE" ? Number(confidence) : 1 - Number(confidence);
}

function gradeFromFakeProbability(pFake) {
  if (pFake === null || Number.isNaN(pFake)) return null;
  if (pFake <= 0.1) return "A";
  if (pFake <= 0.3) return "B";
  if (pFake <= 0.6) return "C";
  if (pFake <= 0.85) return "D";
  return "F";
}

function getGrade(prediction) {
  return prediction?.grade || gradeFromFakeProbability(getFakeProbability(prediction));
}

function getStatus(prediction) {
  return prediction?.status || gradeStyles[getGrade(prediction)]?.status || "PENDING";
}

function getTopWords(prediction) {
  return prediction?.top_indicators || prediction?.important_words || [];
}

function productReviewSummary(data) {
  const reviews = data.reviews || [];
  const analyzed = reviews.filter((review) => review.prediction);
  const fakeProbabilities = analyzed
    .map((review) => getFakeProbability(review.prediction))
    .filter((value) => value !== null && !Number.isNaN(value));
  const rawAverageFakeProbability = fakeProbabilities.length
    ? fakeProbabilities.reduce((sum, value) => sum + value, 0) / fakeProbabilities.length
    : null;
  const confidenceWeight = fakeProbabilities.length
    ? Math.min(fakeProbabilities.length / 20, 1)
    : 0;
  const smallSamplePrior = 0.22;
  const averageFakeProbability = rawAverageFakeProbability === null
    ? null
    : (rawAverageFakeProbability * confidenceWeight) + (smallSamplePrior * (1 - confidenceWeight));
  const realReviews = analyzed.filter((review) => getLabel(review.prediction) !== "FAKE");
  const adjustedBase = realReviews.length ? realReviews : reviews;
  const adjustedRatings = adjustedBase
    .map((review) => Number(review.rating))
    .filter((value) => !Number.isNaN(value));
  const adjustedRating = adjustedRatings.length
    ? adjustedRatings.reduce((sum, value) => sum + value, 0) / adjustedRatings.length
    : null;
  const fakeCount = analyzed.filter((review) => getLabel(review.prediction) === "FAKE").length;
  const grade = gradeFromFakeProbability(averageFakeProbability);

  return {
    grade: grade || "C",
    status: grade ? gradeStyles[grade].status : "PENDING",
    trust: grade ? gradeStyles[grade].trust : "Awaiting analysis",
    fakeCount,
    analyzedCount: analyzed.length,
    adjustedRating,
    averageFakeProbability,
    rawAverageFakeProbability,
    confidenceWeight
  };
}

async function apiPost(path, payload) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || `Request failed: ${path}`);
  return data;
}

function Header({ page, setPage }) {
  return (
    <header className="hero-shell">
      <div>
        <span className="eyebrow">Fake review detection</span>
        <h1 className="dune-title">Amazon Review Analysis Tool</h1>
        <p>
          Product extraction, review inference, confidence scoring, and token-level explanations in one focused interface.
        </p>
      </div>
      <nav className="page-tabs" aria-label="Pages">
        {pages.map((item) => (
          <button
            key={item.id}
            className={page === item.id ? "active" : ""}
            type="button"
            onClick={() => setPage(item.id)}
          >
            <strong>{item.title}</strong>
          </button>
        ))}
      </nav>
    </header>
  );
}

function UrlPanel({ mode, onResult, status, setStatus }) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);

  async function analyze(event) {
    event.preventDefault();
    if (!url.trim()) {
      setStatus("Paste an Amazon product URL first.");
      return;
    }

    setLoading(true);
    try {
      setStatus("Part 1: fetching product JSON using SerpAPI...");
      const productData = await apiPost("/home", { url: url.trim() });
      onResult(productData);

      const endpoint = mode === "ensemble" ? "/predict" : "/text";
      setStatus(mode === "ensemble" ? "Part 2: running ensemble review inference..." : "Part 2: running text-only review inference...");
      const reviews = await analyzeProductReviews(productData.reviews || [], endpoint);
      onResult({ ...productData, reviews });
      setStatus("Analysis complete.");
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="url-panel" onSubmit={analyze}>
      <label htmlFor={`${mode}-url`}>Amazon product URL</label>
      <div className="url-row">
        <input
          id={`${mode}-url`}
          value={url}
          onChange={(event) => setUrl(event.target.value)}
          placeholder="https://www.amazon.com/dp/ASIN..."
        />
        <button type="submit" disabled={loading}>{loading ? "Analyzing" : "Analyze"}</button>
      </div>
      <div className="mini-actions">
        <button type="button" className="quiet" onClick={() => onResult(sampleForMode(mode))}>Load sample</button>
        <span>{status}</span>
      </div>
    </form>
  );
}

async function analyzeProductReviews(reviews, endpoint) {
  const batch = reviews.slice(0, 8);
  const settled = await Promise.allSettled(
    batch.map((review) => {
      const payload =
        endpoint === "/predict"
          ? {
              REVIEW_TEXT: review.text || "",
              RATING: Math.round(Number(review.rating) || 3),
              VERIFIED_PURCHASE: review.verified_purchase ? "Y" : "N"
            }
          : { REVIEW_TEXT: review.text || "" };
      return apiPost(endpoint, payload);
    })
  );

  return reviews.map((review, index) => {
    const result = settled[index];
    return result?.status === "fulfilled" ? { ...review, prediction: result.value } : review;
  });
}

function ProductHero({ data }) {
  const product = data.product || {};
  const images = product.thumbnails || [];
  const [activeImage, setActiveImage] = useState(images[0] || "");
  const image = images.includes(activeImage) ? activeImage : images[0] || "";

  return (
    <section className="product-stage">
      <div className="image-frame">
        {image ? <img src={image} alt={product.title || "Product"} /> : <div className="image-empty">No image</div>}
        <div className="thumbs">
          {images.slice(0, 5).map((src) => (
            <button key={src} type="button" onClick={() => setActiveImage(src)}>
              <img src={src} alt="" />
            </button>
          ))}
        </div>
      </div>
      <article className="product-copy">
        <span className="eyebrow">{valueOrDash(product.brand)}</span>
        <h2>{valueOrDash(product.title)}</h2>
        <div className="price-line">
          <strong>{valueOrDash(product.price)}</strong>
          <span>{valueOrDash(product.old_price)}</span>
          <b>{valueOrDash(product.discount)}</b>
        </div>
        <div className="metric-row">
          <Metric label="Overall rating" value={product.rating} />
          <Metric label="Reviews" value={product.reviews_count} />
          <Metric label="ASIN" value={product.asin} />
          <Metric label="Stock" value={product.stock} />
        </div>
      </article>
    </section>
  );
}

function OverallGradeBanner({ data }) {
  const summary = productReviewSummary(data);
  const grade = summary.grade;

  return (
    <section className={`overall-grade grade-${grade.toLowerCase()}`}>
      <div className="grade-mark">
        <span>{grade}</span>
        <small>Review grade</small>
      </div>
      <div>
        <span className="eyebrow">Overall product trust</span>
        <h2>{summary.status}</h2>
        <p>
          {summary.analyzedCount
            ? `${summary.fakeCount} of ${summary.analyzedCount} analyzed reviews were flagged fake. Grade is softened for limited review samples.`
            : "Run analysis to calculate the product review grade."}
        </p>
      </div>
      <div className="grade-stats">
        <Metric label="Trust level" value={summary.trust} />
        <Metric label="Adjusted rating" value={summary.adjustedRating ? `${summary.adjustedRating.toFixed(1)} stars` : "-"} />
      </div>
    </section>
  );
}

function Metric({ label, value }) {
  return (
    <div className="metric">
      <strong>{valueOrDash(value)}</strong>
      <span>{label}</span>
    </div>
  );
}

function HighlightedTokens({ prediction }) {
  const label = getLabel(prediction);
  const tokens = prediction?.full_token_map || [];
  const topWords = new Set(getTopWords(prediction).slice(0, 6).map((item) => String(item.word).toLowerCase()));
  if (!tokens.length) return <p className="muted">Token highlights will appear after inference runs.</p>;

  return (
    <p className={`token-map ${label.toLowerCase()}`}>
      {tokens.map((token, index) => {
        const score = Number(token.score || 0);
        const important = score >= 0.55 || topWords.has(String(token.word).toLowerCase());
        return (
          <span
            key={`${token.word}-${index}`}
            className={important ? "important" : ""}
            style={{ "--heat": Math.max(0.12, score) }}
            title={`${token.word}: ${score.toFixed(4)}`}
          >
            {token.word}
          </span>
        );
      })}
    </p>
  );
}

function ReviewCard({ review, mode }) {
  const prediction = review.prediction;
  const label = getLabel(prediction);
  const grade = getGrade(prediction);
  const status = getStatus(prediction);
  const topWords = getTopWords(prediction);

  return (
    <article className={`review-card ${label.toLowerCase()} grade-${(grade || "c").toLowerCase()}`}>
      <div className="review-head">
        <div>
          <h3>{valueOrDash(review.title)}</h3>
          <div className="badges">
            <span>{valueOrDash(review.rating)} stars</span>
            <span>{review.verified_purchase ? "Verified purchase" : "Not verified"}</span>
            <span>{valueOrDash(review.date)}</span>
          </div>
        </div>
        <div className={`verdict ${label.toLowerCase()}`}>
          <strong>{label}</strong>
          <span>{status}</span>
          {grade && <b>Grade {grade}</b>}
        </div>
      </div>
      <HighlightedTokens prediction={prediction} />
      <div className="review-foot">
        <span>By {valueOrDash(review.author)}</span>
        <span>{valueOrDash(review.helpful_votes)}</span>
        <span>{mode === "ensemble" ? "Ensemble inference" : "Text-only inference"}</span>
      </div>
      {!!topWords.length && (
        <div className="word-strip">
          {topWords.slice(0, 5).map((item) => (
            <span key={item.word}>{item.word} <b>{Number(item.score).toFixed(2)}</b></span>
          ))}
        </div>
      )}
    </article>
  );
}

function ReviewsFirst({ data, mode }) {
  const reviews = data.reviews || [];
  return (
      <section className="review-zone">
      <div className="section-title">
        <span className="eyebrow">Review inference output</span>
        <h2>Reviews and prediction reasons</h2>
      </div>
      <div className="center-reviews">
        {reviews.length ? reviews.map((review, index) => <ReviewCard key={review.position || index} review={review} mode={mode} />) : <EmptyCard />}
      </div>
    </section>
  );
}

function ProductDetails({ data }) {
  const product = data.product || {};
  const details = product.product_details || {};
  const selectedDetails = detailKeys.filter((key) => details[key]).slice(0, 12);
  const delivery = product.delivery || data.purchase_options?.single_offer?.delivery || [];

  return (
    <section className="detail-grid">
      <article>
        <h3>Relevant product details</h3>
        <div className="info-grid">
          {selectedDetails.map((key) => (
            <div key={key}>
              <span>{key.replaceAll("_", " ")}</span>
              <strong>{details[key]}</strong>
            </div>
          ))}
        </div>
      </article>
      <article>
        <h3>Customer summary</h3>
        <p>{valueOrDash(data.ratings_breakdown?.summary_text)}</p>
        <div className="delivery-list">
          {delivery.map((item) => <span key={item}>{item}</span>)}
        </div>
      </article>
      <article>
        <h3>Similar products</h3>
        <div className="similar-list">
          {(data.similar_products || []).slice(0, 5).map((item) => (
            <div key={item.asin || item.title}>
              <strong>{item.title}</strong>
              <span>{valueOrDash(item.price)} | {valueOrDash(item.rating)} stars | {valueOrDash(item.reviews)} reviews</span>
            </div>
          ))}
        </div>
      </article>
    </section>
  );
}

function ProductInferencePage({ mode }) {
  const [data, setData] = useState(sampleForMode(mode));
  const [status, setStatus] = useState("Sample data loaded.");
  const copy =
    mode === "ensemble"
      ? "Combines product JSON from SerpAPI with review text, rating, and verified purchase metadata."
      : "Combines product JSON from SerpAPI with the text-only model for each review.";

  return (
    <>
      <section className="workflow-card">
        <div>
          <span className="eyebrow">{mode === "ensemble" ? "Page 1" : "Page 2"}</span>
          <h2>{mode === "ensemble" ? "Product page with ensemble inference" : "Product page with text-only inference"}</h2>
          <p>{copy}</p>
        </div>
        <UrlPanel mode={mode} onResult={setData} status={status} setStatus={setStatus} />
      </section>
      <ProductHero data={data} />
      <OverallGradeBanner data={data} />
      <ReviewsFirst data={data} mode={mode} />
      <ProductDetails data={data} />
    </>
  );
}

function StarRatingInput({ value, onChange }) {
  return (
    <div className="star-input" role="radiogroup" aria-label="Rating">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          className={Number(value) >= star ? "active" : ""}
          onClick={() => onChange(star)}
          aria-label={`${star} star`}
        >
          {"\u2605"}
        </button>
      ))}
    </div>
  );
}

function ManualPage() {
  const [reviewText, setReviewText] = useState("Absolutely loved this product! The quality exceeded my expectations and delivery was super fast.");
  const [rating, setRating] = useState(5);
  const [verified, setVerified] = useState("Y");
  const [result, setResult] = useState(sampleProduct.reviews[0].prediction);
  const [status, setStatus] = useState("Ready.");
  const review = useMemo(
    () => ({
      title: "Manual review input",
      rating,
      date: "Now",
      author: "Typed by user",
      verified_purchase: verified === "Y",
      helpful_votes: "Manual check",
      text: reviewText,
      prediction: result
    }),
    [reviewText, rating, verified, result]
  );

  async function submit(event) {
    event.preventDefault();
    setStatus("Running ensemble inference...");
    try {
      const data = await apiPost("/predict", {
        REVIEW_TEXT: reviewText,
        RATING: Math.round(Number(rating) || 3),
        VERIFIED_PURCHASE: verified
      });
      setResult(data);
      setStatus("Manual review analysis complete.");
    } catch (error) {
      setStatus(error.message);
    }
  }

  return (
    <>
      <section className="manual-layout">
        <form className="manual-form" onSubmit={submit}>
          <span className="eyebrow">Page 3</span>
          <h2>Manual ensemble review check</h2>
          <label>Review text</label>
          <textarea value={reviewText} onChange={(event) => setReviewText(event.target.value)} rows="8" />
          <div className="two-col">
            <label>
              Rating
              <StarRatingInput value={rating} onChange={setRating} />
            </label>
            <label>
              Verified purchase
              <select value={verified} onChange={(event) => setVerified(event.target.value)}>
                <option value="Y">Yes</option>
                <option value="N">No</option>
              </select>
            </label>
          </div>
          <button type="submit">Run fake review check</button>
          <span className="status-line">{status}</span>
        </form>
        <div className="manual-result">
          <ReviewCard review={review} mode="ensemble" />
        </div>
      </section>
    </>
  );
}

function EmptyCard() {
  return (
    <article className="review-card">
      <h3>No reviews loaded</h3>
      <p className="muted">Paste an Amazon product URL and run analysis.</p>
    </article>
  );
}

function App() {
  const [page, setPage] = useState("ensemble-product");

  return (
    <main className="app-shell">
      <Header page={page} setPage={setPage} />
      {page === "ensemble-product" && <ProductInferencePage mode="ensemble" />}
      {page === "text-product" && <ProductInferencePage mode="text" />}
      {page === "manual" && <ManualPage />}
    </main>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
