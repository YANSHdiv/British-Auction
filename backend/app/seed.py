import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.rfq import RFQ, RFQStatus
from app.models.auction import AuctionConfiguration, ExtensionTriggerType
from app.models.bid import Bid
from app.models.activity import ActivityLog, ActivityEventType


async def seed_data():
    async with AsyncSessionLocal() as db:
        print("--- Checking and Seeding Demo Data ---")

        # 1. Create Buyer
        buyer_email = "buyer@example.com"
        res = await db.execute(select(User).where(User.email == buyer_email))
        buyer = res.scalars().first()
        if not buyer:
            buyer = User(
                email=buyer_email,
                hashed_password=get_password_hash("password123"),
                full_name="Alex Buyer",
                company_name="Global Freight Procurement Ltd",
                role=UserRole.BUYER
            )
            db.add(buyer)
            await db.flush()
            print(f"Created Buyer: {buyer.email}")

        # 2. Create Suppliers
        suppliers_info = [
            ("supplier1@example.com", "John Swift", "Apex Freight Solutions"),
            ("supplier2@example.com", "Sarah Miller", "BlueDart Express Cargo"),
            ("supplier3@example.com", "Michael Chang", "Continental Shipping & Transit"),
            ("supplier4@example.com", "Elena Rostova", "Delta Global Lines"),
        ]
        suppliers = {}
        for email, name, company in suppliers_info:
            res = await db.execute(select(User).where(User.email == email))
            s = res.scalars().first()
            if not s:
                s = User(
                    email=email,
                    hashed_password=get_password_hash("password123"),
                    full_name=name,
                    company_name=company,
                    role=UserRole.SUPPLIER
                )
                db.add(s)
                await db.flush()
                print(f"Created Supplier: {s.email} ({s.company_name})")
            suppliers[email] = s

        now = datetime.now(timezone.utc)

        # 3. Create RFQ 1: Active British Auction (Clean, ready for live testing)
        rfq1_ref = "RFQ-2026-CHI-DAL"
        res1 = await db.execute(select(RFQ).where(RFQ.reference_id == rfq1_ref))
        if not res1.scalars().first():
            start_time = now - timedelta(minutes=30)
            bid_close = now + timedelta(minutes=20)
            forced_close = now + timedelta(minutes=60)

            rfq1 = RFQ(
                name="Cross-Country Heavy Freight (Chicago to Dallas)",
                reference_id=rfq1_ref,
                pickup_service_date=now + timedelta(days=5),
                status=RFQStatus.ACTIVE,
                buyer_id=buyer.id,
                bid_start_time=start_time,
                bid_close_time=bid_close,
                forced_bid_close_time=forced_close,
            )
            db.add(rfq1)
            await db.flush()

            cfg1 = AuctionConfiguration(
                rfq_id=rfq1.id,
                british_auction_enabled=True,
                trigger_window_minutes=10,
                extension_duration_minutes=5,
                extension_trigger_type=ExtensionTriggerType.BID_RECEIVED,
                current_close_time=bid_close,
                extension_count=0
            )
            db.add(cfg1)

            log1 = ActivityLog(
                rfq_id=rfq1.id,
                event_type=ActivityEventType.RFQ_CREATED,
                metadata_json={"details": "Initial active auction ready for testing."}
            )
            db.add(log1)
            print(f"Created Active RFQ: {rfq1.name}")

        # 4. Create RFQ 2: Active British Auction with existing bids & L1 ranking
        rfq2_ref = "RFQ-2026-DET-ATL"
        res2 = await db.execute(select(RFQ).where(RFQ.reference_id == rfq2_ref))
        if not res2.scalars().first():
            start_time = now - timedelta(hours=1)
            bid_close = now + timedelta(minutes=12)
            forced_close = now + timedelta(minutes=45)

            rfq2 = RFQ(
                name="Automotive Components Expedited Haul (Detroit to Atlanta)",
                reference_id=rfq2_ref,
                pickup_service_date=now + timedelta(days=3),
                status=RFQStatus.ACTIVE,
                buyer_id=buyer.id,
                bid_start_time=start_time,
                bid_close_time=bid_close,
                forced_bid_close_time=forced_close,
            )
            db.add(rfq2)
            await db.flush()

            cfg2 = AuctionConfiguration(
                rfq_id=rfq2.id,
                british_auction_enabled=True,
                trigger_window_minutes=15,
                extension_duration_minutes=5,
                extension_trigger_type=ExtensionTriggerType.L1_RANK_CHANGE,
                current_close_time=bid_close,
                extension_count=0
            )
            db.add(cfg2)

            log2 = ActivityLog(
                rfq_id=rfq2.id,
                event_type=ActivityEventType.RFQ_CREATED,
                metadata_json={"details": "Active RFQ with multiple competitive bids."}
            )
            db.add(log2)

            # Add existing bids
            s1 = suppliers["supplier1@example.com"]
            s2 = suppliers["supplier2@example.com"]
            s3 = suppliers["supplier3@example.com"]

            bid_time_base = now - timedelta(minutes=40)

            # Bid 1: Supplier 3 ($5,200)
            b3 = Bid(
                rfq_id=rfq2.id,
                supplier_id=s3.id,
                carrier_name="Continental Line Express",
                freight_charges=Decimal("4500.00"),
                origin_charges=Decimal("350.00"),
                destination_charges=Decimal("350.00"),
                total_amount=Decimal("5200.00"),
                transit_time_days=2,
                validity_date=now + timedelta(days=14),
                created_at=bid_time_base
            )
            db.add(b3)
            await db.flush()
            db.add(ActivityLog(
                rfq_id=rfq2.id,
                event_type=ActivityEventType.BID_SUBMITTED,
                supplier_id=s3.id,
                bid_id=b3.id,
                metadata_json={"total_amount": "5200.00", "carrier_name": b3.carrier_name},
                created_at=bid_time_base
            ))

            # Bid 2: Supplier 1 ($4,800)
            b1 = Bid(
                rfq_id=rfq2.id,
                supplier_id=s1.id,
                carrier_name="Apex Rapid Fleet",
                freight_charges=Decimal("4200.00"),
                origin_charges=Decimal("300.00"),
                destination_charges=Decimal("300.00"),
                total_amount=Decimal("4800.00"),
                transit_time_days=2,
                validity_date=now + timedelta(days=14),
                created_at=bid_time_base + timedelta(minutes=10)
            )
            db.add(b1)
            await db.flush()
            db.add(ActivityLog(
                rfq_id=rfq2.id,
                event_type=ActivityEventType.BID_SUBMITTED,
                supplier_id=s1.id,
                bid_id=b1.id,
                metadata_json={"total_amount": "4800.00", "carrier_name": b1.carrier_name},
                created_at=bid_time_base + timedelta(minutes=10)
            ))

            # Bid 3: Supplier 2 ($4,500 - Current L1)
            b2 = Bid(
                rfq_id=rfq2.id,
                supplier_id=s2.id,
                carrier_name="BlueDart Logistics Hub",
                freight_charges=Decimal("4000.00"),
                origin_charges=Decimal("250.00"),
                destination_charges=Decimal("250.00"),
                total_amount=Decimal("4500.00"),
                transit_time_days=1,
                validity_date=now + timedelta(days=20),
                created_at=bid_time_base + timedelta(minutes=20)
            )
            db.add(b2)
            await db.flush()
            db.add(ActivityLog(
                rfq_id=rfq2.id,
                event_type=ActivityEventType.BID_SUBMITTED,
                supplier_id=s2.id,
                bid_id=b2.id,
                metadata_json={"total_amount": "4500.00", "carrier_name": b2.carrier_name},
                created_at=bid_time_base + timedelta(minutes=20)
            ))
            print(f"Created RFQ with existing bids: {rfq2.name}")

        # 5. Create RFQ 3: Closed British Auction
        rfq3_ref = "RFQ-2026-PHARMA-BOS"
        res3 = await db.execute(select(RFQ).where(RFQ.reference_id == rfq3_ref))
        if not res3.scalars().first():
            start_time = now - timedelta(days=2)
            bid_close = now - timedelta(hours=3)
            forced_close = now - timedelta(hours=1)

            rfq3 = RFQ(
                name="Pharmaceutical Cold-Chain Air Cargo (Boston to Frankfurt)",
                reference_id=rfq3_ref,
                pickup_service_date=now + timedelta(days=2),
                status=RFQStatus.CLOSED,
                buyer_id=buyer.id,
                bid_start_time=start_time,
                bid_close_time=bid_close,
                forced_bid_close_time=forced_close,
            )
            db.add(rfq3)
            await db.flush()

            cfg3 = AuctionConfiguration(
                rfq_id=rfq3.id,
                british_auction_enabled=True,
                trigger_window_minutes=15,
                extension_duration_minutes=10,
                extension_trigger_type=ExtensionTriggerType.ANY_RANK_CHANGE,
                current_close_time=bid_close,
                extension_count=1
            )
            db.add(cfg3)

            s4 = suppliers["supplier4@example.com"]
            b4 = Bid(
                rfq_id=rfq3.id,
                supplier_id=s4.id,
                carrier_name="Delta Global Cold Express",
                freight_charges=Decimal("7500.00"),
                origin_charges=Decimal("300.00"),
                destination_charges=Decimal("300.00"),
                total_amount=Decimal("8100.00"),
                transit_time_days=1,
                validity_date=now + timedelta(days=7),
                created_at=now - timedelta(hours=4)
            )
            db.add(b4)
            await db.flush()

            db.add(ActivityLog(
                rfq_id=rfq3.id,
                event_type=ActivityEventType.AUCTION_CLOSED,
                old_close_time=bid_close,
                new_close_time=bid_close,
                extension_reason="Auction concluded normally at bid close time.",
                created_at=bid_close
            ))
            print(f"Created Closed RFQ: {rfq3.name}")

        # 6. Create RFQ 4: Force-Closed British Auction (Hit hard limit)
        rfq4_ref = "RFQ-2026-GRAIN-GULF"
        res4 = await db.execute(select(RFQ).where(RFQ.reference_id == rfq4_ref))
        if not res4.scalars().first():
            start_time = now - timedelta(days=1)
            bid_close = now - timedelta(hours=6)
            forced_close = now - timedelta(hours=5)

            rfq4 = RFQ(
                name="Bulk Agricultural Grain Shipment (Midwest to Gulf Port)",
                reference_id=rfq4_ref,
                pickup_service_date=now + timedelta(days=7),
                status=RFQStatus.FORCE_CLOSED,
                buyer_id=buyer.id,
                bid_start_time=start_time,
                bid_close_time=bid_close,
                forced_bid_close_time=forced_close,
            )
            db.add(rfq4)
            await db.flush()

            cfg4 = AuctionConfiguration(
                rfq_id=rfq4.id,
                british_auction_enabled=True,
                trigger_window_minutes=10,
                extension_duration_minutes=5,
                extension_trigger_type=ExtensionTriggerType.BID_RECEIVED,
                current_close_time=forced_close,  # Reached forced close!
                extension_count=3
            )
            db.add(cfg4)

            db.add(ActivityLog(
                rfq_id=rfq4.id,
                event_type=ActivityEventType.AUCTION_FORCE_CLOSED,
                old_close_time=forced_close,
                new_close_time=forced_close,
                extension_reason="Auction reached mandatory Forced Bid Close Time. All bidding terminated unconditionally.",
                created_at=forced_close
            ))
            print(f"Created Force-Closed RFQ: {rfq4.name}")

        await db.commit()
        print("--- Seed Completed Successfully! ---")


if __name__ == "__main__":
    asyncio.run(seed_data())
